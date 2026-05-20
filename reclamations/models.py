from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from equipes.models import Equipe

class Reclamation(models.Model):

    # STATUTS
    STATUTS = [

        ('en_attente', 'En attente'),

        ('en_cours', 'En cours'),

        ('traitee', 'Traitée'),

        ('rejetee', 'Rejetée'),

    ]

    # TYPES DE RECOURS
    TYPES = [

        ('arbitrage', 'Mauvais arbitrage'),

        ('discipline', 'Problème disciplinaire'),

        ('joueur', 'Joueur non qualifié'),

        ('organisation', 'Organisation'),

        ('violence', 'Violence'),

        ('autre', 'Autre'),

    ]

    # DECISIONS COMMISSION
    DECISIONS = [

        ('accepte', 'Accepté'),

        ('rejete', 'Rejeté'),

        ('partiel', 'Accepté partiellement'),

    ]

    # UTILISATEUR
    utilisateur = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # EQUIPE
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # TYPE DE RECOURS
    type_reclamation = models.CharField(
        max_length=50,
        choices=TYPES
    )

    # DESCRIPTION
    description = models.TextField()

    # PIECE JOINTE UTILISATEUR
    fichier_joint = models.FileField(
        upload_to='recours/',
        null=True,
        blank=True
    )

    # STATUT DOSSIER
    statut = models.CharField(
        max_length=20,
        choices=STATUTS,
        default='en_attente'
    )

    # DECISION COMMISSION
    decision_commission = models.CharField(
        max_length=20,
        choices=DECISIONS,
        null=True,
        blank=True
    )

    # COMMENTAIRE ADMIN
    commentaire_admin = models.TextField(
        null=True,
        blank=True
    )

    # DOCUMENT OFFICIEL FINAL
    document_final = models.FileField(
        upload_to='decisions/',
        null=True,
        blank=True
    )

    # DATE CREATION
    date = models.DateTimeField(
        auto_now_add=True
    )

    # DATE TRAITEMENT
    date_traitement = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):

        return (
            f"{self.utilisateur.username} - "
            f"{self.get_type_reclamation_display()}"
        )

class ReclamationCommentaire(models.Model):
    reclamation = models.ForeignKey(Reclamation, on_delete=models.CASCADE, related_name="commentaires")
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)