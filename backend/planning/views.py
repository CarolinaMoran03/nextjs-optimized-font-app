from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import PlanningRequest
from .serializers import PlanningRequestSerializer
import io
from django.http import FileResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.conf import settings
import os

class PlanningRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PlanningRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'admin':
            return PlanningRequest.objects.all()
        return PlanningRequest.objects.filter(created_by=user)

    def perform_create(self, serializer):
        planning = serializer.save()
        self.generate_planning_pdf(planning)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        planning = self.get_object()
        self.generate_planning_pdf(planning)
        return Response({'message': 'Planificación regenerada exitosamente'})

    def generate_planning_pdf(self, planning):
        """
        Generate PDF for the planning request using AI-generated content
        """
        try:
            # Update status to processing
            planning.status = 'processing'
            planning.save()

            # Here you would typically call your AI service
            # For now, we'll create a simple template
            context = {
                'planning': planning,
                'subjects': [s.strip() for s in planning.subjects.split(',')],
            }

            # Render HTML content
            html_string = render_to_string('planning/planning_template.html', context)

            # Create PDF
            output = io.BytesIO()
            pdf = pisa.CreatePDF(html_string, dest=output)

            if not pdf.err:
                # Save PDF to FileField
                filename = f'planning_{planning.id}.pdf'
                planning.generated_pdf.save(filename, output)
                planning.status = 'completed'
                planning.save()
            else:
                planning.status = 'failed'
                planning.error_message = 'Error al generar el PDF'
                planning.save()

        except Exception as e:
            planning.status = 'failed'
            planning.error_message = str(e)
            planning.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_planning(request, planning_id):
    planning = get_object_or_404(PlanningRequest, id=planning_id)
    
    # Check permissions
    if request.user.profile.role != 'admin' and planning.created_by != request.user:
        return Response(
            {'error': 'No autorizado para descargar esta planificación'},
            status=status.HTTP_403_FORBIDDEN
        )

    if not planning.generated_pdf:
        return Response(
            {'error': 'No se ha generado el PDF para esta planificación'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        response = FileResponse(
            planning.generated_pdf.open('rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(planning.generated_pdf.name)}"'
        return response
    except Exception as e:
        return Response(
            {'error': f'Error al descargar el archivo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
