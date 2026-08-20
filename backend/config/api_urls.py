from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.api_views import (
    RegisterAPIView, LoginAPIView, LogoutAPIView, 
    UserProfileAPIView, DashboardAPIView
)
from category.api_views import CategoryViewSet
from expenses.api_views import ExpenseViewSet
from budget.api_views import BudgetViewSet, BudgetAllocationViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'expenses', ExpenseViewSet, basename='expense')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'budget-allocations', BudgetAllocationViewSet, basename='budget-allocation')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
    path('auth/profile/', UserProfileAPIView.as_view(), name='api-profile'),
    
    # Dashboard summary statistics
    path('dashboard/', DashboardAPIView.as_view(), name='api-dashboard'),
    
    # Router endpoints (CRUD)
    path('', include(router.urls)),
]
