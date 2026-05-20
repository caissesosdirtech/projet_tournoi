from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from equipes.models import Equipe


class Reclamation(models.Model):

    STATUTS = [
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('traitee', 'Traitée'),
        ('rejetee', 'Rejetée'),
    ]

    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)

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
    fichier_joint = models.FileField(upload_to='reclamations/', null=True, blank=True)

    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')

    decision = models.TextField(blank=True)

    document_final = models.FileField(upload_to='reclamations/final/', null=True, blank=True)

    vu_par_user = models.BooleanField(default=False)

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.equipe.nom} - {self.auteur.username}"


class ReclamationCommentaire(models.Model):
    reclamation = models.ForeignKey(Reclamation, on_delete=models.CASCADE, related_name="commentaires")
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)