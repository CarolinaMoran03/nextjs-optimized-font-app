from django.contrib import admin
from .models import PlanningRequest

@admin.register(PlanningRequest)
class PlanningRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_by',
        'course',
        'planning_type',
        'start_date',
        'end_date',
        'status',
        'created_at'
    )
    list_filter = ('status', 'planning_type', 'created_at')
    search_fields = (
        'created_by__username',
        'created_by__email',
        'course',
        'subjects'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'generated_pdf',
        'error_message'
    )
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or request.user.profile.role == 'admin':
            return qs
        return qs.filter(created_by=request.user)

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or request.user.profile.role == 'admin' or obj.created_by == request.user

    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return True
        return request.user.is_superuser or request.user.profile.role == 'admin' or obj.created_by == request.user

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
