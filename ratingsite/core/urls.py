from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # ← THIS LINE INCLUDES YOUR CORE APP URLs
]

# Serve media files
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Serve static files
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
