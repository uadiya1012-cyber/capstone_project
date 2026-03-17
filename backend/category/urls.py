from django.urls import path
from . import views

app_name = 'category'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('create/', views.category_create, name='create'),
    path('<int:pk>/', views.category_detail, name='detail'),
    path('<int:pk>/edit/', views.category_edit, name='edit'),
    path('<int:pk>/delete/', views.category_delete, name='delete'),
]
