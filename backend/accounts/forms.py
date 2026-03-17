from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    # add email field to registration form
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            # If your CustomUser.email already has unique=True, this check is optional
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise forms.ValidationError("Энэ имэйл хаяг аль хэдийн ашиглагдсан байна.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user

