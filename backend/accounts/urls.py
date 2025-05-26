from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.get_user_profile, name='profile'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('create-admin/', views.create_default_admin, name='create-admin'),
]
