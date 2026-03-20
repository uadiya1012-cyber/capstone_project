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


@login_required
def user_dashboard(request):
    """Энэ view нь хэрэглэгчийн dashboard-г харуулах бөгөөд эндээс хэрэглэгч category, budget, expense-ийг нэг дор үүсгэх боломжтой. POST хүсэлт ирсэн тохиолдолд, form-уудыг шалгаж, хэрэв зөв бол transaction.atomic() блок дотор бүх объектыг хадгална. GET хүсэлт ирсэн тохиолдолд хоосон form-уудыг үүсгэнэ. Мөн expense формын category сонголтыг зөвхөн global болон тухайн хэрэглэгчийн категориудаар хязгаарлана.
    """
    if request.method == 'POST':
        # Distinguish between creating a standalone category and creating all 3 items.
        cat_form = CategoryForm(request.POST, prefix='cat')
        bud_form = BudgetForm(request.POST, prefix='bud')
        exp_form = ExpenseForm(request.POST, request.FILES, prefix='exp')

        # If user clicked the standalone "create category" button
        if 'create_category' in request.POST:
            if cat_form.is_valid():
                new_cat = cat_form.save(commit=False)
                new_cat.user = request.user
                new_cat.save()
            return redirect('user_dashboard')

        # If user submitted the combined quick-create forms
        if cat_form.is_valid() and bud_form.is_valid() and exp_form.is_valid():
            with transaction.atomic():
                category = cat_form.save(commit=False)
                category.user = request.user
                category.save()

                budget = bud_form.save(commit=False)
                budget.user = request.user
                if not budget.category:
                    budget.category = category
                budget.save()

                expense = exp_form.save(commit=False)
                expense.user = request.user
                if not expense.category:
                    expense.category = category
                if not expense.budget:
                    expense.budget = budget
                if 'receipt' in request.FILES:
                    expense.receipt = request.FILES['receipt']
                expense.save()

            return redirect('user_dashboard')
    else:
        cat_form = CategoryForm(prefix='cat')
        bud_form = BudgetForm(prefix='bud')
        exp_form = ExpenseForm(prefix='exp')

    # Restrict expense category choices to global + user's categories
    try:
        exp_form.fields['category'].queryset = Category.objects.filter(Q(user__isnull=True) | Q(user=request.user))
    except Exception:
        # In case form initialization failed earlier, ignore and continue
        pass

    return render(request, 'accounts/user_dashboard.html', {
        'cat_form': cat_form,
        'bud_form': bud_form,
        'exp_form': exp_form,
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
