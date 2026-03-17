from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, help_text='The user who created this category. Null for default categories.')
    description = models.TextField(blank=True)
    is_income = models.BooleanField(default=False) # Зарцуулалтын категори эсвэл орлогын категори болохыг заана
    color = models.CharField(max_length=7,blank=True, help_text='Hex color code for category visualization')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name') # Нэг хэрэглэгчийн хувьд категори нэр давтагдахгүй байх.
        ordering = ['name'] # Категори нэрээр эрэмбэлэх
        indexes = [
            models.Index(fields=['user', 'name']), # Хэрэглэгч ба нэрийн индекс хайлт хурдасгах
        ]

    def __str__(self):
        owner = 'Global' if self.user is None else str(self.user)
        return f"{self.name} ({owner})"
    
# Категори нь хэрэглэгчийн үүсгэсэн эсвэл глобал (системийн) категори байж болно. Глобал категори нь бүх хэрэглэгчид ашиглах боломжтой бөгөөд хэрэглэгчийн үүсгэсэн категори нь тухайн хэрэглэгчид л харагдах болно.