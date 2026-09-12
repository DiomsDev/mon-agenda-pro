from django.contrib import admin
from django.urls import path, include

from agenda.views import service_worker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('comptes/', include('comptes.urls')),
    path('service-worker.js', service_worker, name='service_worker'),
    path('', include('agenda.urls')),
]