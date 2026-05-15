from .models import Match, Equipe, Joueur, But
from django.db.models import Count



def notifications(request):

    # nombre total d'équipes
    total_equipes = Equipe.objects.count()

    # nombre total de matchs
    total_matchs = Match.objects.count()

    # nombre total de joueurs
    total_joueurs = Joueur.objects.count()

    # meilleur buteur
    meilleur_buteur = Joueur.objects.annotate(
        nb_buts=Count('but')
    ).order_by('-nb_buts').first()

    return {
        'total_equipes': total_equipes,
        'total_matchs': total_matchs,
        'total_joueurs': total_joueurs,
        'meilleur_buteur': meilleur_buteur,
    }


def equipes_menu(request):
    equipes = Equipe.objects.all()
    return {
        'equipes_menu': equipes
    }