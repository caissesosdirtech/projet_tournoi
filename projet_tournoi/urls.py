# projet_tournoi/projet_tournoi/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('matchs.urls')),  # toutes les URLs de ton app matchs
]
