from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('create/', views.budget_create, name='budget_create'),
    path('<int:pk>/', views.budget_detail, name='budget_detail'),
    path('<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    path('<int:pk>/delete/', views.budget_delete, name='budget_delete'),
    path('<int:budget_pk>/allocation/add/', views.allocation_add, name='allocation_add'),
]
