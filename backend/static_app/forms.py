from django import forms
from .models import StaticApp

class StaticAppForm(forms.ModelForm):
    class Meta:
        model = StaticApp
        fields = '__all__'


from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'phone', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }