from django.contrib import admin
from .models import Budget, BudgetAllocation

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'total_amount', 'start_date', 'end_date')
    list_filter = ('user',)
    search_fields = ('name',)

@admin.register(BudgetAllocation)
class BudgetAllocationAdmin(admin.ModelAdmin):
    list_display = ('budget', 'category', 'amount')
