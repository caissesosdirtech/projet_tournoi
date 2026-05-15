from equipes.models import Equipe
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Reclamation(models.Model):
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)  # Utilisation FK pour la liste déroulante
    type_reclamation = models.CharField(
        max_length=50,
        choices=[
            ('arbitrage', 'Arbitrage'),
            ('joueur', 'Joueur non qualifié'),
            ('organisation', 'Organisation'),
            ('autre', 'Autre')
        ]
    )
    description = models.TextField(blank=True)
    fichier_joint = models.FileField(upload_to='reclamations/', blank=True, null=True)
    
    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('en_cours', 'En cours'),
            ('traitee', 'Traitée')
        ],
        default='en_attente'
    )
    
    decision = models.TextField(blank=True)  # commentaire admin
    document_final = models.FileField(upload_to='reclamations/final/', blank=True, null=True)
    
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Réclamation {self.equipe.nom} - {self.auteur.username}"