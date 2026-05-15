from django.urls import path
from .views import discipline


urlpatterns = [
    path('discipline/', discipline, name='discipline'),
]