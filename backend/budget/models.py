from django.db import models
from django.conf import settings
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')  # Хэрэглэгчтэй холбоотой болох нэмэлт талбар
    name = models.CharField(max_length=120)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00')) # Нийт төсвийн хэмжээ
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('category.Category', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-start_date']  # Төсвийг эхлэх огноогоор буурахаар эрэмбэлэх
        unique_together = ('user', 'name', 'start_date')  # Нэг хэрэглэгчийн хувьд төсвийн нэр ба эхлэх огноо давтагдахгүй байх
    
    def __str__(self):
        return f"{self.name} - {self.user}" 
    
# Төсвийн загвар нь хэрэглэгчтэй холбоотой байх бөгөөд нэг хэрэглэгч олон төсөв үүсгэх боломжтой. Нийт төсвийн хэмжээ, эхлэх болон дуусах огноо, тэмдэглэл зэрэг талбаруудыг агуулна. Төсвүүд эхлэх огноогоор эрэмбэлэгдэж, нэг хэрэглэгчийн хувьд нэр ба эхлэх огноо давтагдахгүй байх зохицуулалттай.

# Доорх нь BudgetAllocation загварын эхний хувилбар бөгөөд энэ нь төсвийн тодорхой хэсэгт мөнгө хуваарилах зориулалттай. Энэ загвар нь тухайн төсөвтэй холбоотой байх бөгөөд хуваарилсан хэмжээ, огноо, тайлбар зэрэг талбаруудыг агуулна.
class BudgetAllocation(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='allocations') # Төсөвтэй холбоотой болох нэмэлт талбар
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE) # Категоритой холбоотой болох нэмэлт талбар
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00')) # Хувиарилсан хэмжээ

    class Meta:
        unique_together = ('budget', 'category')  # Нэг төсөвт нэг категори давтагдахгүй байх



