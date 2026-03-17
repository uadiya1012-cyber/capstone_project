from django.contrib import admin
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_income', 'created_at')
    list_filter = ('is_income', 'user')
    search_fields = ('name',)
