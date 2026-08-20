from rest_framework import viewsets, permissions
from .models import Budget, BudgetAllocation
from .serializers import BudgetSerializer, BudgetAllocationSerializer

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return budgets belonging to the authenticated user
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically assign the logged-in user to the new budget
        serializer.save(user=self.request.user)


class BudgetAllocationViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return allocations for budgets belonging to the authenticated user
        return BudgetAllocation.objects.filter(budget__user=self.request.user)
