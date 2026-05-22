from .models import Equipe

def get_equipes():
    return Equipe.objects.all()

def is_capitaine_ou_coach(user):
    return user.groups.filter(name__in=['Capitaines', 'Coachs']).exists()