from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Count


# ============================
# 🏟️ EQUIPE
# ============================
class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)

    coach_principal = models.CharField(max_length=100)
    coach_adjoint = models.CharField(max_length=100)

    points = models.IntegerField(default=0)
    buts_encaisses = models.IntegerField(default=0)  # Gardé uniquement les buts encaissés

    def difference_buts(self):
        return self.buts_marques_total - self.buts_encaisses

    @property
    def buts_marques_total(self):
        """
        Somme des buts marqués par tous les joueurs de l'équipe
        """
        return self.joueurs.aggregate(total=Count('buts'))['total'] or 0

    def clean(self):
        if self.joueurs.count() < 25:
            raise ValidationError("Chaque équipe doit avoir au minimum 25 joueurs.")

    def __str__(self):
        return self.nom


# ============================
# 🧑‍🤝‍🧑 JOUEUR
# ============================
class Joueur(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name="joueurs")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero = models.IntegerField()
    poste = models.CharField(max_length=50)

    cartons_jaunes = models.IntegerField(default=0)
    cartons_rouges = models.IntegerField(default=0)
    suspendu = models.BooleanField(default=False)

    def verifier_suspension(self):
        if self.cartons_rouges > 0 or self.cartons_jaunes >= 2:
            self.suspendu = True
        else:
            self.suspendu = False
        self.save()

    def __str__(self):
        return f"{self.nom} ({self.equipe.nom})"


# ============================
# ⚽ MATCH
# ============================
class Match(models.Model):
    STATUT_CHOICES = [
        ('A_VENIR', 'À venir'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
        ('ANNULE', 'Annulé'),
    ]

    equipe1 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='matchs_equipe1')
    equipe2 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='matchs_equipe2')
    date = models.DateTimeField()
    score1 = models.IntegerField(default=0)
    score2 = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='A_VENIR')

    def __str__(self):
        return f"{self.equipe1.nom} vs {self.equipe2.nom} ({self.date.strftime('%d/%m/%Y')})"


# ============================
# 📝 RÉCLAMATION
# ============================
class Reclamation(models.Model):
    equipe = models.ForeignKey(Equipe, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    message = models.TextField()

    STATUT = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('rejetee', 'Rejetée'),
    ]

    statut = models.CharField(max_length=20, choices=STATUT, default='en_attente')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réclamation - {self.equipe.nom}"


# ============================
# 🟨🟥⚽ ÉVÉNEMENTS DE MATCH
# ============================
class EvenementMatch(models.Model):
    TYPE_EVENEMENT = [
        ('BUT', 'But'),
        ('CJ', 'Carton Jaune'),
        ('CR', 'Carton Rouge'),
    ]

    match = models.ForeignKey(
        Match,
        related_name="evenements",
        on_delete=models.CASCADE
    )

    joueur = models.ForeignKey(
        Joueur,
        related_name="evenements",
        on_delete=models.CASCADE
    )

    type_evenement = models.CharField(max_length=3, choices=TYPE_EVENEMENT)
    minute = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.joueur} - {self.get_type_evenement_display()}"


# ============================
# ⚽ BUT
# ============================
class But(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE, related_name='buts')
    minute = models.IntegerField()

    def __str__(self):
        return f"{self.joueur.equipe.nom} - {self.joueur.nom} ({self.match})"

    def equipe_joueur(self):
        return f"{self.joueur.equipe.nom} - {self.joueur.nom}"
    equipe_joueur.short_description = "Équipe - Joueur"
