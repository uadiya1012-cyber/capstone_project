from django import forms
from django.db.models import Q
from .models import Budget, BudgetAllocation
from category.models import Category

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'start_date', 'end_date', 'total_amount', 'notes', 'category']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).order_by('name')

class BudgetAllocationForm(forms.ModelForm):
    class Meta:
        model = BudgetAllocation
        fields = ['category', 'amount']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).order_by('name')