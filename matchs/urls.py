from django.urls import path, include  # <-- ajoute include ici
from django.urls import path
from . import views

urlpatterns = [

    # ================= DASHBOARD & ACCUEIL =================
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # ================= AUTHENTIFICATION ADMIN =================
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),

    # ================= MATCHS =================
    path('programmer-match/', views.programmer_match, name='programmer_match'),
    path('calendrier/', views.calendrier, name='calendrier'),
    path('resultats/', views.resultats, name='resultats'),
    path('match/<int:id>/evenements/', views.gerer_evenements, name='gerer_evenements'),
    path('match/<int:id>/supprimer/', views.supprimer_match, name='supprimer_match'),
    
    # ================= CLASSEMENTS & STATS =================
    path('classement/', views.classement, name='classement'),
    path('stats-equipes/', views.stats_equipes, name='stats_equipes'),
    path('stats-joueurs/', views.stats_joueurs, name='stats_joueurs'),

    # ================= INFORMATIONS =================
    path('infos/', views.infos, name='infos'),
    path('ajouter-info/', views.ajouter_info, name='ajouter_info'),
    path('galeries/', views.galeries, name='galeries'), 


    # ================= GESTION EQUIPES =================
    path('equipes/', views.liste_equipes, name='liste_equipes'),
    path('dashboard/equipe/ajouter/', views.ajouter_equipe, name='ajouter_equipe'),
    path('equipes/<int:id>/editer/', views.editer_equipe, name='editer_equipe'),
    path('equipes/<int:id>/supprimer/', views.supprimer_equipe, name='supprimer_equipe'),
    path('equipes/<int:equipe_id>/', views.detail_equipe, name='detail_equipe'),


    # ================= GESTION JOUEURS =================

    path('joueurs/', views.liste_joueurs, name='liste_joueurs'),
    path('dashboard/joueur/ajouter/', views.ajouter_joueur, name='ajouter_joueur'),
    path('joueur/ajouter/', views.ajouter_joueur, name='ajouter_joueur'),
    path('joueurs/<int:id>/editer/', views.editer_joueur, name='editer_joueur'),
    path('joueur/editer/<int:id>/', views.editer_joueur, name='editer_joueur'),
    path('joueur/supprimer/<int:id>/', views.supprimer_joueur, name='supprimer_joueur'),
    path('joueur/modifier/<int:id>/', views.editer_joueur, name='modifier_joueur'),


    # ================= GESTION GALERIES =================

   path('galerie/', views.galeries, name='galeries'),
   path('galerie/ajouter/', views.ajouter_media, name='ajouter_media'),
   path('galerie/archiver/<int:media_id>/', views.archiver_media, name='archiver_media'),
   path('galerie/archives/', views.medias_archives, name='medias_archives'),
   path("galerie/supprimer/", views.supprimer_media, name="supprimer_media"),
   path("galerie/restaurer/<int:id>/", views.restaurer_media, name="restaurer_media"),
   path("galerie/supprimer-definitif/<int:id>/", views.supprimer_definitif_media, name="supprimer_definitif_media"),

    # ================= REGLEMENT INTERIEUR =================

   path('reglement/', views.reglement_interieur, name='reglement_interieur'),

       # ================= TELECHARGEMENT PDF/WORD =================


   path('telecharger/pdf/', views.telecharger_pdf, name='telecharger_pdf'),
   path('telecharger/word/', views.telecharger_word, name='telecharger_word'),
   path('telecharger/odf/', views.telecharger_odf, name='telecharger_odf'),
]
