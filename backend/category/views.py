from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, models
from .forms import CategoryForm
from accounts.decorators import role_required
from django.contrib import messages

@login_required
def category_list(request):
    # Global categories (user is none) болон нийтэд зориулсан категориудыг харуулах
    categories = Category.objects.filter(models.Q(user__isnull=True) | models.Q(user=request.user)).order_by('name')
    return render(request, 'category/category_list.html', {'categories': categories})

@login_required
def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    # Хэрэв категори нь хэрэгчтэй холбоотой бол эзэмшигч эсэхийг шалгана
    if category.user is not None and category.user != request.user:
        messages.error(request, 'You do not have permission to view this category.')
        return redirect('category:category_list')
    return render(request, 'category/category_detail.html', {'category': category})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user # Категорийг тухайн хэрэглэгчид холбох
            category.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category:category_list')
    else:
        form = CategoryForm()
    return render(request, 'category/category_form.html', {'form': form})
    
@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if category.user is not None and category.user != request.user:
        messages.error(request, 'You do not have permission to edit this category.')
        return redirect('category:category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category/category_form.html', {'form': form, 'category': category})

@login_required
@role_required(allowed_roles=['ADMIN', 'MODERATOR'])
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    # Админ болон Модератор зөвхөн хэрэглэгчийн категориудыг устгах боломжтой
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('category:category_list')
    return render(request, 'category/category_confirm_delete.html', {'category': category})
