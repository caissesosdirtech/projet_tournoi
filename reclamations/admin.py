from django.contrib import admin
from .models import Reclamation

@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'equipe', 'type_reclamation', 'statut', 'date', 'fichier_joint')
    list_filter = ('statut', 'date')
    search_fields = ('equipe', 'description')