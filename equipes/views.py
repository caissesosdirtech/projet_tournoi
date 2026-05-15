from django.shortcuts import render, get_object_or_404
from .models import Equipe

def detail_equipe(request, id):
    equipe = get_object_or_404(Equipe, id=id)
    return render(request, 'equipes/detail_equipe.html', {
        'equipe': equipe
    })
