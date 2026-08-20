import json
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import transaction
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm, UserProfileForm
from .decorators import role_required

# Forms for combined quick-create
from category.forms import CategoryForm
from budget.forms import BudgetForm
from expenses.forms import ExpenseForm
from category.models import Category
from django.db.models import Q

User = get_user_model()


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save(commit=False)
                user.is_active = False  # Deactivate account until email verification
                user.save()
            
            # Send activation email
            current_site = get_current_site(request)
            domain = current_site.domain
            protocol = 'https' if request.is_secure() else 'http'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            mail_subject = 'Бүртгэлээ баталгаажуулна уу - Expense Tracker'
            context = {
                'user': user,
                'domain': domain,
                'uid': uid,
                'token': token,
                'protocol': protocol,
            }
            message_html = render_to_string('accounts/activation_email.html', context)
            message_txt = render_to_string('accounts/activation_email.txt', context)
            
            email = EmailMultiAlternatives(
                mail_subject,
                message_txt,
                to=[user.email]
            )
            email.attach_alternative(message_html, "text/html")
            email.send()
            
            return redirect('registration_pending')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def registration_pending(request):
    return render(request, 'accounts/registration_pending.html')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Таны бүртгэл амжилттай баталгаажлаа!')
        return redirect('user_dashboard')
    else:
        return render(request, 'accounts/activation_failed.html')



def get_chart_data(user):
    from datetime import datetime, date, timedelta
    import calendar
    from django.db.models import Sum
    from expenses.models import Expense
    from budget.models import Budget
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_date = date.today()
    
    # --- Monthly Expenses (Line Chart) ---
    monthly_data = []
    for month in range(1, 13):
        total = Expense.objects.filter(
            user=user, 
            date__year=current_year, 
            date__month=month
        ).exclude(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0.00
        monthly_data.append(float(total))
        
    # --- Category Doughnut Chart ---
    category_data = Expense.objects.filter(user=user).exclude(category__is_income=True).values('category__name').annotate(total=Sum('amount')).order_by('-total')[:5]
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
    
    # === REPORTS TAB DATA ===
    
    # --- This month vs Previous month expenses ---
    this_month_total = Expense.objects.filter(
        user=user, date__year=current_year, date__month=current_month
    ).exclude(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0.00
    this_month_total = float(this_month_total)
    
    prev_month = current_month - 1
    prev_year = current_year
    if prev_month == 0:
        prev_month = 12
        prev_year = current_year - 1
    
    prev_month_total = Expense.objects.filter(
        user=user, date__year=prev_year, date__month=prev_month
    ).exclude(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or 0.00
    prev_month_total = float(prev_month_total)
    
    month_change_percent = 0
    if prev_month_total > 0:
        month_change_percent = round(((this_month_total - prev_month_total) / prev_month_total) * 100, 1)
    
    # --- Top 5 Categories (this year) for horizontal bar ---
    top5_cat_data = Expense.objects.filter(
        user=user, date__year=current_year
    ).exclude(category__is_income=True).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')[:5]
    
    top5_labels = [item['category__name'] or 'Бусад' for item in top5_cat_data]
    top5_values = [float(item['total']) for item in top5_cat_data]
    
    # --- Daily average spending this month ---
    days_passed = current_date.day
    daily_avg = round(this_month_total / max(days_passed, 1), 0)
    
    # --- Total transactions count ---
    total_tx_count = Expense.objects.filter(user=user).count()
    
    return {
        'monthly_data': monthly_data,
        'cat_labels': cat_labels,
        'cat_values': cat_values,
        'budget_labels': budget_labels,
        'budget_allocated': budget_allocated,
        'budget_spent': budget_spent,
        # Reports
        'this_month_total': this_month_total,
        'prev_month_total': prev_month_total,
        'month_change_percent': month_change_percent,
        'top5_labels': top5_labels,
        'top5_values': top5_values,
        'daily_avg': daily_avg,
        'total_tx_count': total_tx_count,
    }



@login_required
def user_dashboard(request):
    """Энэ view нь хэрэглэгчийн dashboard-г харуулна."""
    import json
    from datetime import datetime
    today_date = datetime.now().date()
    
    cat_form = CategoryForm(request.POST if 'create_category' in request.POST else None, prefix='cat')
    bud_form = BudgetForm(request.POST if 'create_budget' in request.POST else None, prefix='bud', user=request.user)
    exp_form = ExpenseForm(
        request.POST if 'create_expense' in request.POST else None,
        request.FILES if 'create_expense' in request.POST else None,
        prefix='exp',
        initial={'date': today_date},
        user=request.user
    )
    prof_form = UserProfileForm(
        request.POST if 'update_profile' in request.POST else None,
        request.FILES if 'update_profile' in request.POST else None,
        instance=request.user,
        prefix='prof'
    )

    if request.method == 'POST':
        if 'create_expense' in request.POST:
            if exp_form.is_valid():
                expense = exp_form.save(commit=False)
                expense.user = request.user
                expense.save()
                messages.success(request, 'Зардал амжилттай бүртгэгдлээ!')
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
        elif 'update_profile' in request.POST:
            if prof_form.is_valid():
                prof_form.save()
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
        
    # Calculate dynamic stats
    from django.db.models import Sum
    from datetime import datetime
    from decimal import Decimal
    from expenses.models import Expense, CommonExpense
    from budget.models import Budget
    
    current_time = datetime.now()
    current_year = current_time.year
    current_month = current_time.month
    current_date = current_time.date()

    # Total Income (Category is_income = True)
    total_income = Expense.objects.filter(
        user=request.user,
        category__is_income=True
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Total Expense (Category is_income = False or Category is NULL)
    total_expense = Expense.objects.filter(
        user=request.user
    ).exclude(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    total_balance = float(total_income - total_expense)

    # Monthly Expenses (only expenses this month)
    monthly_expenses = Expense.objects.filter(
        user=request.user,
        date__year=current_year,
        date__month=current_month
    ).exclude(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    monthly_expenses = float(monthly_expenses)

    # Today's Expenses (only expenses today)
    today_expenses = Expense.objects.filter(
        user=request.user,
        date=current_date
    ).exclude(category__is_income=True).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    today_expenses = float(today_expenses)

    daily_limit_exceeded = False
    if request.user.daily_limit > 0 and today_expenses > float(request.user.daily_limit):
        daily_limit_exceeded = True

    # Active Budgets for this month
    active_budgets = Budget.objects.filter(
        user=request.user,
        start_date__lte=current_date,
        end_date__gte=current_date
    )
    monthly_budget = active_budgets.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00')
    monthly_budget = float(monthly_budget)

    # Active budgets data list for UI rendering
    active_budgets_data = []
    for b in active_budgets:
        spent = Expense.objects.filter(user=request.user, budget=b).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        spent = float(spent)
        total = float(b.total_amount)
        percent = min((spent / total) * 100, 100) if total > 0 else 0
        active_budgets_data.append({
            'name': b.name,
            'total': total,
            'spent': spent,
            'remaining': max(total - spent, 0),
            'percent': percent,
            'percent_formatted': f"{percent:.1f}"
        })

    # Recent Transactions (last 10 transactions)
    recent_transactions = Expense.objects.filter(user=request.user).select_related('category').order_by('-date', '-created_at')[:10]

    # Fetch common expenses
    common_expenses = CommonExpense.objects.all().select_related('category')

    chart_data = get_chart_data(request.user)

    return render(request, 'accounts/user_dashboard.html', {
        'cat_form': cat_form if 'create_category' in request.POST or request.method == 'GET' else CategoryForm(prefix='cat'),
        'bud_form': bud_form if 'create_budget' in request.POST or request.method == 'GET' else BudgetForm(prefix='bud', user=request.user),
        'exp_form': exp_form if 'create_expense' in request.POST or request.method == 'GET' else ExpenseForm(prefix='exp', initial={'date': today_date}, user=request.user),
        'prof_form': prof_form if 'update_profile' in request.POST or request.method == 'GET' else UserProfileForm(instance=request.user, prefix='prof'),
        'chart_data_json': chart_data,
        'total_balance': total_balance,
        'monthly_expenses': monthly_expenses,
        'monthly_budget': monthly_budget,
        'active_budgets_data': active_budgets_data,
        'recent_transactions': recent_transactions,
        'common_expenses': common_expenses,
        'daily_limit_exceeded': daily_limit_exceeded,
        'today_expenses': today_expenses,
    })


@login_required
@role_required(allowed_roles=['ADMIN', 'MODERATOR'])
def moderator_dashboard(request):
    return render(request, 'accounts/moderator_dashboard.html')


@login_required
@role_required(allowed_roles=['ADMIN'])
def admin_settings(request):
    return render(request, 'accounts/admin_settings.html')


@login_required
@require_POST
def delete_expense(request, pk):
    """Хэрэглэгчийн зардлыг устгах."""
    from expenses.models import Expense
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, 'Зардал амжилттай устгагдлаа!')
    return redirect('user_dashboard')


@login_required
def edit_expense(request, pk):
    """Хэрэглэгчийн зардлыг засварлах (GET: JSON мэдээлэл буцаах, POST: хадгалах)."""
    from expenses.models import Expense
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    
    if request.method == 'GET':
        # Return expense data as JSON for the edit modal
        return JsonResponse({
            'id': expense.pk,
            'amount': str(expense.amount),
            'category_id': expense.category_id or '',
            'description': expense.description or '',
            'date': expense.date.isoformat(),
            'is_recurring': expense.is_recurring,
            'recurring_interval': expense.recurring_interval or '',
        })
    
    elif request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense, prefix='edit', user=request.user)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.user = request.user
            updated.save()
            messages.success(request, 'Зардал амжилттай шинэчлэгдлээ!')
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Алдаа гарлаа. Мэдээллээ шалгана уу.')
            return redirect('user_dashboard')


#  Энд код нь хэрэглэгчийн бүртгэл, dashboard, moderator болон admin view-уудыг агуулж байна.
