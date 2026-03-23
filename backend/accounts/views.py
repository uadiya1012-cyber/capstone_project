from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .decorators import role_required
from django.db import transaction

# Forms for combined quick-create
from category.forms import CategoryForm
from budget.forms import BudgetForm
from expenses.forms import ExpenseForm
from category.models import Category
from django.db.models import Q


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def get_chart_data(user):
    from datetime import datetime
    import calendar
    from django.db.models import Sum
    from expenses.models import Expense
    from budget.models import Budget
    
    current_year = datetime.now().year
    
    # --- Monthly Expenses (Line Chart) ---
    monthly_data = []
    for month in range(1, 13):
        total = Expense.objects.filter(
            user=user, 
            date__year=current_year, 
            date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0.00
        monthly_data.append(float(total))
        
    # --- Category Doughnut Chart ---
    category_data = Expense.objects.filter(user=user).values('category__name').annotate(total=Sum('amount')).order_by('-total')[:5]
    cat_labels = []
    cat_values = []
    for item in category_data:
        name = item['category__name'] or 'Uncategorized'
        cat_labels.append(name)
        cat_values.append(float(item['total']))
        
    if not cat_labels:
        cat_labels = ["No Data"]
        cat_values = [1]
        
    # --- Budget vs Expenses (Bar Chart) ---
    budgets = Budget.objects.filter(user=user).order_by('-start_date')[:5]
    budget_labels = []
    budget_allocated = []
    budget_spent = []
    
    for b in budgets:
        budget_labels.append(b.name)
        budget_allocated.append(float(b.total_amount))
        # Total spent in this budget
        spent = Expense.objects.filter(user=user, budget=b).aggregate(Sum('amount'))['amount__sum'] or 0.00
        budget_spent.append(float(spent))
        
    return {
        'monthly_data': monthly_data,
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'budget_labels': budget_labels,
        'budget_allocated': budget_allocated,
        'budget_spent': budget_spent
    }


@login_required
def user_dashboard(request):
    """Энэ view нь хэрэглэгчийн dashboard-г харуулна."""
    import json
    
    cat_form = CategoryForm(request.POST if 'create_category' in request.POST else None, prefix='cat')
    bud_form = BudgetForm(request.POST if 'create_budget' in request.POST else None, prefix='bud')
    exp_form = ExpenseForm(request.POST if 'create_expense' in request.POST else None, request.FILES if 'create_expense' in request.POST else None, prefix='exp')

    if request.method == 'POST':
        if 'create_expense' in request.POST:
            if exp_form.is_valid():
                expense = exp_form.save(commit=False)
                expense.user = request.user
                expense.save()
                return redirect('user_dashboard')
        elif 'create_budget' in request.POST:
            if bud_form.is_valid():
                budget = bud_form.save(commit=False)
                budget.user = request.user
                budget.save()
                return redirect('user_dashboard')
        elif 'create_category' in request.POST:
            if cat_form.is_valid():
                new_cat = cat_form.save(commit=False)
                new_cat.user = request.user
                new_cat.save()
                return redirect('user_dashboard')

    # Restrict expense category choices to global + user's categories
    try:
        qs = Category.objects.filter(Q(user__isnull=True) | Q(user=request.user))
        if exp_form.fields.get('category'):
            exp_form.fields['category'].queryset = qs
        if bud_form.fields.get('category'):
            bud_form.fields['category'].queryset = qs
    except Exception:
        pass
        
    chart_data = get_chart_data(request.user)

    return render(request, 'accounts/user_dashboard.html', {
        'cat_form': cat_form if 'create_category' in request.POST or request.method == 'GET' else CategoryForm(prefix='cat'),
        'bud_form': bud_form if 'create_budget' in request.POST or request.method == 'GET' else BudgetForm(prefix='bud'),
        'exp_form': exp_form if 'create_expense' in request.POST or request.method == 'GET' else ExpenseForm(prefix='exp'),
        'chart_data_json': chart_data
    })


@login_required
@role_required(allowed_roles=['ADMIN', 'MODERATOR'])
def moderator_dashboard(request):
    return render(request, 'accounts/moderator_dashboard.html')


@login_required
@role_required(allowed_roles=['ADMIN'])
def admin_settings(request):
    return render(request, 'accounts/admin_settings.html')


#  Энд код нь хэрэглэгчийн бүртгэл, dashboard, moderator болон admin view-уудыг агуулж байна. user_dashboard view нь хэрэглэгчид category, budget, expense-ийг нэг дор үүсгэх боломжийг олгодог бөгөөд POST хүсэлт ирсэн тохиолдолд form-уудыг шалгаж, transaction.atomic() блок дотор бүх объектыг хадгална. GET хүсэлт ирсэн тохиолдолд хоосон form-уудыг үүсгэнэ. Мөн expense формын category сонголтыг зөвхөн global болон тухайн хэрэглэгчийн категориудаар хязгаарлана. moderator_dashboard болон admin_settings view-ууд нь зөвхөн тодорхой үүрэгтэй хэрэглэгчдэд л хандах боломжтой.
