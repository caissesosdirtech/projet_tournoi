from django.db import models
from equipes.models import Equipe

class Joueur(models.Model):
    POSTE_CHOICES = [
        ('GK', 'Gardien'),
        ('DF', 'Défenseur'),
        ('MF', 'Milieu'),
        ('FW', 'Attaquant'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.PositiveIntegerField()
    poste = models.CharField(max_length=2, choices=POSTE_CHOICES)
    photo = models.ImageField(upload_to='joueurs/', null=True, blank=True)
    
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.CASCADE,
        related_name='joueurs'
    )

    suspendu = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['numero', 'equipe'],
                name='unique_numero_par_equipe'
            )
        ]
        ordering = ['equipe', 'numero']  # optionnel mais pro

    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.equipe.nom})"