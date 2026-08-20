from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MODERATOR', 'Moderator'),
        ('USER', 'User'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    currency = models.CharField(max_length=5, default='₮')
    daily_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    monthly_savings_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        # Hide role in string representation to avoid showing it in logs/UI
        return f"{self.username}"
    

# Энд код нь CustomUser загварыг AbstractUser-аас өвлөн авч, role гэсэн шинэ талбар нэмсэн. ROLE_CHOICES нь хэрэглэгчийн үүрэг сонголтуудыг тодорхойлдог. __str__() метод нь хэрэглэгчийн нэрийг буцаадаг бөгөөд үүргийг харуулахгүйгээр string representation-ыг хянадаг. Хэрэглэгч бүртгүүлэх үед role choice хийх шаарлага байхгүй гэж default утга USER гэж зааж өгсөн.