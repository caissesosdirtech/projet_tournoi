from django.db import models
from django.db.models import Sum


class Equipe(models.Model):
    nom = models.CharField(max_length=100)
    coach1 = models.CharField(max_length=100)
    coach2 = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    # =============================
    # AFFICHAGE NOM EQUIPE
    # =============================
    def __str__(self):
        return self.nom

    # =============================
    # BUTS MARQUES
    # =============================
    @property
    def buts_marques_total(self):
        total1 = self.matchs1.filter(statut='joue').aggregate(total=Sum('score1'))['total'] or 0
        total2 = self.matchs2.filter(statut='joue').aggregate(total=Sum('score2'))['total'] or 0
        return total1 + total2

    # =============================
    # BUTS ENCAISSES
    # =============================
    @property
    def buts_encaisses_total(self):
        total1 = self.matchs1.filter(statut='joue').aggregate(total=Sum('score2'))['total'] or 0
        total2 = self.matchs2.filter(statut='joue').aggregate(total=Sum('score1'))['total'] or 0
        return total1 + total2

    # =============================
    # POINTS
    # =============================
    @property
    def points(self):
        points = 0

        # matchs où l'équipe est equipe1
        for match in self.matchs1.filter(statut='joue'):
            s1 = match.score1 or 0
            s2 = match.score2 or 0

            if s1 > s2:
                points += 3
            elif s1 == s2:
                points += 1

        # matchs où l'équipe est equipe2
        for match in self.matchs2.filter(statut='joue'):
            s1 = match.score1 or 0
            s2 = match.score2 or 0

            if s2 > s1:
                points += 3
            elif s2 == s1:
                points += 1

        return points