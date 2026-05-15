from django.urls import path
from . import views
from reclamations import views as reclamations_views



urlpatterns = [

         # ================= GESTION RECLAMATIONS =================

    path('liste/', views.liste_reclamations, name='liste_reclamations'),
    path('creer/', views.creer_reclamation, name='creer_reclamation'),
    path('login/', views.login_reclamation, name='login_reclamation'),
    path('', views.liste_reclamations, name='liste_reclamations'),
    path('<int:id>/decision/', views.decision_reclamation, name='decision_reclamation'),
    path('reclamation/supprimer/<int:id>/', views.supprimer_reclamation, name='supprimer_reclamation'),
    

]

