from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Budget, BudgetAllocation
from .forms import BudgetForm, BudgetAllocationForm
from django.contrib import messages
from accounts.decorators import role_required

@login_required
def budget_list(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-start_date')
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully.')
            return redirect('budget:budget_detail', pk=budget.pk)
    else:
        form = BudgetForm()
    context = {
        'budgets': budgets,
        'form': form
    }
    return render(request, 'budget/budget_list.html', context)

@login_required
def budget_detail(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    allocations = budget.allocations.select_related('category').all()
    return render(request, 'budget/budget_detail.html', {'budget': budget, 'allocations': allocations})

@login_required
def budget_create(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            messages.success(request, 'Budget created successfully.')
            return redirect('budget:budget_detail', pk=budget.pk)
    else:
        form = BudgetForm()
    return render(request, 'budget/budget_form.html', {'form': form})

@login_required
def budget_edit(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Budget updated successfully.')
            return redirect('budget:budget_detail', pk=budget.pk)
    else:
        form = BudgetForm(instance=budget)
    return render(request, 'budget/budget_form.html', {'form': form, 'budget': budget})

@login_required
@role_required(allowed_roles=['ADMIN', 'MODERATOR'])
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully.')
        return redirect('budget:budget_list')
    return render(request, 'budget/budget_confirm_delete.html', {'budget': budget})


# Optionally add allocation to a budget
@login_required
def allocation_add(request, budget_pk):
    budget = get_object_or_404(Budget, pk=budget_pk, user=request.user)
    if request.method == 'POST':
        form = BudgetAllocationForm(request.POST)
        if form.is_valid():
            allocation = form.save(commit=False)
            allocation.budget = budget
            allocation.save()
            messages.success(request, 'Allocation added successfully.')
            return redirect('budget:budget_detail', pk=budget.pk)
    else:
        form = BudgetAllocationForm()
    return render(request, 'budget/allocation_form.html', {'form': form, 'budget': budget})

