from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    list_display = ['username', 'email', 'first_name', 'last_name', 'role']

admin.site.register(CustomUser, CustomUserAdmin)