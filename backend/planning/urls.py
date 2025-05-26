from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'requests', views.PlanningRequestViewSet, basename='planning-request')

app_name = 'planning'

urlpatterns = [
    path('', include(router.urls)),
    path('download/<int:planning_id>/', views.download_planning, name='download-planning'),
]
