from django.db import models
from django.conf import settings
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses') # Хэрэглэгчтэй холбоотой болох нэмэлт талбар
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.ForeignKey('category.Category', on_delete=models.SET_NULL, null=True, blank=True) # Категоритой холбоотой болох нэмэлт талбар
    date = models.DateField()
    description = models.TextField(blank=True)
    receipt = models.ImageField(upload_to='receipts/%Y/%m/%d/', blank=True, null=True) # Баримтын зураг хадгалах талбар
    budget = models.ForeignKey('budget.Budget', on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses') # Төсөвтэй холбоотой нэмэлт талбар
    is_recurring = models.BooleanField(default=False) # Давтамжтай зардал эсэхийг заах талбар
    created_at = models.DateTimeField(auto_now_add=True) # Зардал үүссэн огноо

    class Meta:
        ordering = ['-date', '-created_at'] # Зардлыг огноо болон үүссэн огноогоор буурахаар эрэмбэлэх
        indexes = [
            models.Index(fields=['user', 'date']), # Хэрэглэгч ба огнооны индекс хайлт хурдасгах
            models.Index(fields=['category']), # Категорийн индекс хайлт хурдасгах
        ]

    def __str__(self):
        return f"{self.user} - {self.amount} on {self.date}"