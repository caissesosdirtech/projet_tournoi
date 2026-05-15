from .models import Equipe

def get_equipes():
    return Equipe.objects.all()