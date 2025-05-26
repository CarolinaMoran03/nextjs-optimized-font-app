from rest_framework import serializers
from .models import PlanningRequest
from accounts.serializers import UserSerializer

class PlanningRequestSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    planning_type_display = serializers.CharField(source='get_planning_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PlanningRequest
        fields = (
            'id',
            'created_by',
            'subjects',
            'course',
            'start_date',
            'end_date',
            'planning_type',
            'planning_type_display',
            'number_units',
            'generated_pdf',
            'created_at',
            'updated_at',
            'status',
            'status_display',
            'error_message'
        )
        read_only_fields = (
            'created_by',
            'generated_pdf',
            'created_at',
            'updated_at',
            'status',
            'error_message'
        )

    def validate(self, attrs):
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError({
                "dates": "La fecha de inicio debe ser anterior a la fecha de fin"
            })
        return attrs

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
