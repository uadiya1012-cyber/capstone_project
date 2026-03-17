from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone

@login_required
def expense_list(request):
    qs = Expense.objects.filter(user=request.user).select_related('category', 'budget')
    # Optional filtering by date or category via GET params
    category_id = request.GET.get('category')
    start = request.GET.get('start')
    end = request.GET.get('end')
    if category_id:
        qs = qs.filter(category_id=category_id)
    if start:
        qs = qs.filter(date__gte=start)
    if end:
        qs = qs.filter(date__lte=end)
    total = qs.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
    return render(request, 'expenses/expense_list.html', {'expenses': qs.order_by('-date'), 'total': total})

@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    return render(request, 'expenses/expense_detail.html', {'expense': expense})


@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense created successfully.')
            return redirect('expenses:expense_list')
    else:
        form = ExpenseForm(initial={'date': timezone.localdate()})
    return render(request, 'expenses/expense_form.html', {'form': form})

@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('expenses:expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'expenses/expense_form.html', {'form': form, 'expense': expense})

@login_required
def expense_delete(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect('expenses:expense_list')
    return render(request, 'expenses/expense_confirm_delete.html', {'expense': expense})

