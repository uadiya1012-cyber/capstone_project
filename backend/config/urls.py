from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz/', views.healthz, name='healthz'),  # платформын health check
    path('', include('static_app.urls')),
    path('accounts/', include('accounts.urls')),
    path('category/', include('category.urls')),
    path('expenses/', include('expenses.urls')),
    path('budget/', include('budget.urls')),
    path('api/v1/', include('config.api_urls')),
]

if settings.DEBUG:
    # Локал хөгжүүлэлт: Django өөрөө media-г шалгалтгүй үйлчилнэ.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: `static()` helper нь DEBUG=False үед ХООСОН жагсаалт буцаадаг
    # тул /media/ маршрут бүрмөсөн байхгүй болж, аватар/баримтын зураг 404
    # болно. Иймд эрхийн шалгалттай өөрийн view-г тавина (config/views.py).
    urlpatterns += [
        path('media/<path:path>', views.protected_media, name='protected_media'),
    ]
