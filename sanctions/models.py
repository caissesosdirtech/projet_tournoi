from django.db import models
from joueurs.models import Joueur
from matchs.models import Match
from equipes.models import Equipe

class Carton(models.Model):
    TYPE_CHOICES = [
        ('jaune', 'Jaune'),
        ('rouge', 'Rouge'),
    ]

    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE, related_name='sanctions_cartons')
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    minute = models.IntegerField()

    def __str__(self):
        return f"{self.joueur} - {self.type}"

# sanctions/models.py

class Suspension(models.Model):
    joueur = models.ForeignKey(
        Joueur,
        on_delete=models.CASCADE,
        related_name="suspensions"   # 🔥 IMPORTANT
    )
    actif = models.BooleanField(default=True)
    matchs_restants = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    match_declencheur = models.ForeignKey(Match, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.joueur} suspendu ({self.matchs_restants})" 
          
