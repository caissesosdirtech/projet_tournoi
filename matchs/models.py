from django.db import models
from equipes.models import Equipe
from joueurs.models import Joueur
from django.utils import timezone

class Match(models.Model):
    STATUT_CHOICES = [
        ('programme', 'Programmé'),
        ('en_cours', 'En cours'),
        ('joue', 'Joué'),
    ]

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='programme')
    equipe1 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='matchs1')
    equipe2 = models.ForeignKey(Equipe, on_delete=models.CASCADE, related_name='matchs2')
    stade = models.CharField(max_length=150)
    date = models.DateTimeField()
    score1 = models.IntegerField(null=True, blank=True)
    score2 = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # S'assure que la date est aware avant de sauvegarder
        if timezone.is_naive(self.date):
            self.date = timezone.make_aware(self.date)
        super().save(*args, **kwargs)

    @property
    def statut_auto(self):
        now = timezone.now()
        if self.score1 is not None and self.score2 is not None:
            return 'termine'
        elif self.date <= now:
            return 'en_cours'
        else:
            return 'a_venir'

    def __str__(self):
        return f"{self.equipe1.nom} vs {self.equipe2.nom}"
        

class But(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='buts')
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE, related_name='buts')
    minute = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.joueur.nom} ({self.minute}')"


class Carton(models.Model):
    TYPE_CHOICES = [
        ('jaune', 'Jaune'),
        ('rouge', 'Rouge'),
    ]
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='cartons')
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE, related_name='matchs_cartons')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    minute = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.type} - {self.joueur.nom} ({self.minute}')"

class Evenement(models.Model):
    TYPE_CHOICES = [
        ('but', 'But'),
        ('carton_jaune', 'Carton jaune'),
        ('carton_rouge', 'Carton rouge'),
        ('suspension', 'Suspension'),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='evenements')
    joueur = models.ForeignKey(Joueur, on_delete=models.CASCADE)
    type_evenement = models.CharField(max_length=30, choices=TYPE_CHOICES)
    minute = models.IntegerField()

    def __str__(self):
        return f"{self.type_evenement} - {self.joueur} ({self.minute}’)"

class InfoTournoi(models.Model):
    PRIORITE_CHOICES = [
        ('urgent', 'Urgent'),
        ('important', 'Important'),
        ('information', 'Information'),
    ]

    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='information')
    date_publication = models.DateTimeField(auto_now_add=True)
    equipe = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, blank=True)  # optionnel
    fichier = models.FileField(upload_to='infos/', null=True, blank=True)


    def __str__(self):
        return self.titre


class Notification(models.Model):
    TYPE_NOTIFICATION = [
        ('report', 'Match reporté'),
        ('buteur', 'Nouveau meilleur buteur'),
        ('fin_match', 'Match terminé'),
        ('info', 'Information'),
    ]
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=20, choices=TYPE_NOTIFICATION)
    date_creation = models.DateTimeField(auto_now_add=True)
    equipe = models.ForeignKey(Equipe, on_delete=models.SET_NULL, null=True, blank=True)  # optionnel  

    def __str__(self):
        return self.titre

class Galerie (models.Model):

    TYPE_CHOICES = [
        ('photo', 'Photo'),
        ('video', 'Vidéo')
    ]

    titre = models.CharField(max_length=200, blank=True)
    type_media = models.CharField(max_length=10, choices=TYPE_CHOICES)
    image = models.ImageField(upload_to='galerie/photos/', blank=True, null=True, max_length=300)
    video = models.FileField(upload_to='galerie/videos/', blank=True, null=True, max_length=300)
    date_ajout = models.DateTimeField(auto_now_add=True)
    archive = models.BooleanField(default=False)
    

    def __str__(self):
        return self.titre or "Media"