from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('static_app.urls')),
    path('accounts/', include('accounts.urls')),
    path('category/', include('category.urls')),
    path('expenses/', include('expenses.urls')),
    path('budget/', include('budget.urls')),
]

# Serve media files during development when DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

