from django import forms
from django.db.models import Q
from .models import Expense
from category.models import Category
from budget.models import Budget

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['amount', 'category', 'date', 'description', 'receipt', 'budget', 'is_recurring', 'recurring_interval']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user__isnull=True) | Q(user=user)
            ).order_by('name')
            self.fields['budget'].queryset = Budget.objects.filter(user=user).order_by('-start_date')