from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

    list_display = ['username', 'email', 'first_name', 'last_name', 'role']

admin.site.register(CustomUser, CustomUserAdmin)

# Энд код нь CustomUserAdmin классийг UserAdmin-аас өвлөн авч, fieldsets-д шинэ хэсэг нэмсэн бөгөөд list_display-д role-г нэмсэн. Энд CustomUser загварыг CustomUserAdmin-ээр бүртгэж байна. Энэ нь Django админд хэрэглэгчийн мэдээллийг илүү дэлгэрэнгүй харах боломжийг олгоно.