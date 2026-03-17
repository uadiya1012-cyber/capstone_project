from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('moderator/', views.moderator_dashboard, name='moderator_dashboard'),
    path('admin-settings/', views.admin_settings, name='admin_settings'),
]