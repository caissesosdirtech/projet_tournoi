# equipes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('<int:id>/', views.detail_equipe, name='detail_equipe'),
]
