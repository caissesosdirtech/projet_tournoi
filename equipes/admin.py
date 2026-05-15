from django.contrib import admin
from .models import Equipe

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'coach1', 'coach2')
    search_fields = ('nom', 'coach1', 'coach2')


