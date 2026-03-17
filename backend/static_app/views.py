from django.shortcuts import render

def info(request):
    return render(request, 'static_app/info.html')

def contact(request):
    return render(request, 'static_app/contact.html')


def home(request):
    return render(request, 'static_app/home.html')

