from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .export_views import export_csv, export_pdf

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('register/', views.register, name='register'),
    path('register/pending/', views.registration_pending, name='registration_pending'),
    path('activate/<str:uidb64>/<str:token>/', views.activate, name='activate'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('moderator/', views.moderator_dashboard, name='moderator_dashboard'),
    path('admin-settings/', views.admin_settings, name='admin_settings'),
    # Export
    path('export/csv/', export_csv, name='export_csv'),
    path('export/pdf/', export_pdf, name='export_pdf'),
    # Expense management
    path('expense/<int:pk>/delete/', views.delete_expense, name='delete_expense'),
    path('expense/<int:pk>/edit/', views.edit_expense, name='edit_expense'),
]