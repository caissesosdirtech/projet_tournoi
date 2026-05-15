# projet_tournoi/urls.py
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('matchs.urls')), 
    path('reclamations/', include('reclamations.urls')), 
    path('sanctions/', include('sanctions.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)