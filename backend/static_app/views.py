from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def info(request):
    return render(request, 'static_app/info.html')

def contact(request):
    # Allow anonymous visitors to submit contact/feedback messages.
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. Thank you!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'static_app/contact.html', {'form': form})


def home(request):
    return render(request, 'static_app/home.html')

