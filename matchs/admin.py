from django.contrib import admin
from .models import Match, InfoTournoi
from .models import Galerie


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):

    list_display = ('equipe1', 'equipe2', 'date', 'score1', 'score2', 'statut')

    list_filter = ('statut',)


from django.contrib import admin
from .models import InfoTournoi, Notification


@admin.register(InfoTournoi)
class InfoTournoiAdmin(admin.ModelAdmin):
    list_display = ('titre', 'priorite', 'date_publication')
    search_fields = ('titre', 'contenu')
    list_filter = ('priorite',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'type_notification', 'date_creation')
    list_filter = ('type_notification',)
    search_fields = ('titre', 'message') 


@admin.register(Galerie)
class GalerieAdmin(admin.ModelAdmin):

    list_display = ('titre','type_media','date_ajout')
    list_filter = ('type_media',)    
