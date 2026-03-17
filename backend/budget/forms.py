from django import forms
from .models import Budget, BudgetAllocation

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'start_date', 'end_date', 'total_amount', 'notes', 'category']

class BudgetAllocationForm(forms.ModelForm):
    class Meta:
        model = BudgetAllocation
        fields = ['budget', 'category', 'amount']