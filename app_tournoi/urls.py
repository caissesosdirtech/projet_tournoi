# app_tournoi/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('matchs.urls')), 
    path( '', views.dashboard, name='dashboard'),
    path('calendrier/', views.calendrier, name='calendrier'),
    path('resultats/', views.resultats, name='resultats'),  # <-- ici !
    path('galeries/', views.galeries, name='galeries'),      # <-- ici !
    path('equipes/<int:equipe_id>/', views.detail_equipe, name='detail_equipe'),
    path('classement/', views.classement, name='classement'),
    path('infos/', views.infos, name='infos'),
    path('stats/equipes/', views.stats_equipes, name='stats_equipes'),
    path('stats/joueurs/', views.stats_joueurs, name='stats_joueurs'),
    path('reclamations/', views.reclamation, name='reclamation'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/matchs/', views.admin_matchs, name='admin_matchs'),
    path('admin/match/<int:id>/', views.admin_match_detail, name='admin_match_detail'),
    path('admin/equipes/', views.admin_equipes, name='admin_equipes'),
    path('admin/joueurs/<int:equipe_id>/', views.admin_joueurs, name='admin_joueurs'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
]


