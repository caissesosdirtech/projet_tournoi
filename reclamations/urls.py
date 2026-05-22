from django.urls import path
from . import views

urlpatterns = [

    # ================= DASHBOARD USER =================
    path(
        'dashboard/',
        views.recours_dashboard,
        name='recours_dashboard'
    ),

    # ================= LOGIN RECOURS =================
    path(
        'login/',
        views.login_reclamation,
        name='login_reclamation'
    ),

    path(
        'recours/logout/',
        views.logout_reclamation, 
        name='logout_reclamation'
    ),

    # ================= CREER RECOURS =================
    path(
        'creer/',
        views.creer_reclamation,
        name='creer_reclamation'
    ),

    # ================= MES RECOURS =================
    path(
        'mes-recours/',
        views.mes_reclamations,
        name='mes_reclamations'
    ),

    # ================= COMMENTAIRE =================
    path(
        'commentaire/<int:id>/',
        views.ajouter_commentaire,
        name='ajouter_commentaire'
    ),

    # ================= ADMIN =================
    path(
        'liste/',
        views.liste_reclamations,
        name='liste_reclamations'
    ),

    path(
        'decision/<int:id>/',
        views.decision_reclamation,
        name='decision_reclamation'
    ),

    path(
        'supprimer/<int:id>/',
        views.supprimer_reclamation,
        name='supprimer_reclamation'
    ),
]