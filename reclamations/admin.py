from django.contrib import admin
from .models import Reclamation


@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):

    list_display = (

        'utilisateur',

        'equipe',

        'type_reclamation',

        'statut',

        'decision_commission',

        'date'

    )

    list_filter = (

        'statut',

        'decision_commission',

        'type_reclamation'

    )

    search_fields = (

        'utilisateur__username',

        'equipe__nom',

    )