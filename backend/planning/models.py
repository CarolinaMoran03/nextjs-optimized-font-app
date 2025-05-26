from django.db import models
from django.contrib.auth.models import User

class PlanningRequest(models.Model):
    PLANNING_TYPES = (
        ('anual', 'Anual'),
        ('microcurricular', 'Microcurricular'),
        ('semanal', 'Semanal'),
    )
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    subjects = models.CharField(max_length=255, help_text="Materias separadas por comas")
    course = models.CharField(max_length=100, help_text="Nivel o grado de impartición")
    start_date = models.DateField()
    end_date = models.DateField()
    planning_type = models.CharField(max_length=20, choices=PLANNING_TYPES)
    number_units = models.PositiveIntegerField(help_text="Número de unidades a impartir")
    generated_pdf = models.FileField(upload_to='planifications/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pendiente'),
            ('processing', 'Procesando'),
            ('completed', 'Completado'),
            ('failed', 'Fallido'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_by.username} - {self.get_planning_type_display()} - {self.created_at.date()}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError('La fecha de inicio debe ser anterior a la fecha de fin.')
