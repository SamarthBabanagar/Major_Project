from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views  # import your local core/views.py

urlpatterns = [
    path('', views.home, name='home'),             # Homepage
    path('admin/', admin.site.urls),               # Django admin
    path('patients/', include('patients.urls')),   # Patients app
    path('accounts/', include('accounts.urls')),   # Aadhaar & login system
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
