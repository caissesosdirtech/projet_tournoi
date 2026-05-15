from django.contrib import admin
from .models import Match, EvenementMatch, Equipe, Joueur, But

class EvenementInline(admin.TabularInline):
    model = EvenementMatch
    extra = 1

@admin.register(But)
class ButAdmin(admin.ModelAdmin):
    list_display = ('equipe_joueur', 'match', 'minute')
    list_filter = ('match', 'joueur__equipe')
