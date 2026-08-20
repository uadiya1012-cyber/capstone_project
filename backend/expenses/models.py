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
    RECURRING_INTERVAL_CHOICES = (
        ('', 'Давтамжгүй'),
        ('daily', 'Өдөр бүр'),
        ('weekly', '7 хоног бүр'),
        ('monthly', 'Сар бүр'),
    )
    recurring_interval = models.CharField(max_length=10, choices=RECURRING_INTERVAL_CHOICES, blank=True, default='')
    next_recurrence_date = models.DateField(null=True, blank=True) # Дараагийн автомат үүсгэлийн огноо
    created_at = models.DateTimeField(auto_now_add=True) # Зардал үүссэн огноо

    class Meta:
        ordering = ['-date', '-created_at'] # Зардлыг огноо болон үүссэн огноогоор буурахаар эрэмбэлэх
        indexes = [
            models.Index(fields=['user', 'date']), # Хэрэглэгч ба огнооны индекс хайлт хурдасгах
            models.Index(fields=['category']), # Категорийн индекс хайлт хурдасгах
        ]

    def __str__(self):
        return f"{self.user} - {self.amount} on {self.date}"

    def save(self, *args, **kwargs):
        # If updating an existing instance, check if fields affecting recurrence changed
        if self.pk:
            try:
                old = Expense.objects.get(pk=self.pk)
                if (old.date != self.date or 
                    old.is_recurring != self.is_recurring or 
                    old.recurring_interval != self.recurring_interval):
                    self.next_recurrence_date = None
            except Expense.DoesNotExist:
                pass

        # Calculate next_recurrence_date if it is recurring and date is set
        if self.is_recurring and self.recurring_interval:
            if self.next_recurrence_date is None:
                from datetime import timedelta
                if self.recurring_interval == 'daily':
                    self.next_recurrence_date = self.date + timedelta(days=1)
                elif self.recurring_interval == 'weekly':
                    self.next_recurrence_date = self.date + timedelta(weeks=1)
                elif self.recurring_interval == 'monthly':
                    month = self.date.month
                    year = self.date.year
                    if month == 12:
                        self.next_recurrence_date = self.date.replace(year=year+1, month=1)
                    else:
                        try:
                            self.next_recurrence_date = self.date.replace(month=month+1)
                        except ValueError:
                            import calendar
                            last_day = calendar.monthrange(year, month+1)[1]
                            self.next_recurrence_date = self.date.replace(month=month+1, day=last_day)
        else:
            self.next_recurrence_date = None

        super().save(*args, **kwargs)


class CommonExpense(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey('category.Category', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name