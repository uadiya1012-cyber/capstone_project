from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('static_app.urls')),
    path('accounts/', include('accounts.urls')),
    path('category/', include('category.urls')),
    path('expenses/', include('expenses.urls')),
    path('budget/', include('budget.urls')),
]

