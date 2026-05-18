# app_tournoi/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Equipe, Match, Reclamation
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from joueurs.models import Joueur




def liste_equipes(request):
    equipes = Equipe.objects.all()
    return render(request, 'tournoi/liste_equipes.html', {'equipes': equipes})

def detail_equipe(request, equipe_id):
    equipe = get_object_or_404(Equipe, id=equipe_id)
    joueurs = equipe.joueurs.all()  # relation ManyToMany ou ForeignKey
    matchs = Match.objects.filter(teams__in=[equipe])  # si relation ManyToMany
    # Statistiques cumulées
    stats = {
        'buts_marques': sum(j.buts for j in joueurs),
        'cartons_jaunes': sum(j.cartons_jaunes for j in joueurs),
        'cartons_rouges': sum(j.cartons_rouges for j in joueurs),
        'buts_encaisse': sum(m.score_adverse(equipe) for m in matchs)  # méthode à définir
    }
    return render(request, 'tournoi/detail_equipe.html', {
        'equipe': equipe,
        'joueurs': joueurs,
        'stats': stats,
        'matchs': matchs
    })

def liste_joueurs(request):
    joueurs = Joueur.objects.all()
    return render(request, 'tournoi/liste_joueurs.html', {'joueurs': joueurs})

def liste_matchs(request):
    matchs = Match.objects.order_by("date")
    return render(request, 'tournoi/liste_matchs.html', {'matchs': matchs})

def detail_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return render(request, 'tournoi/detail_match.html', {'match': match})

def classement(request):
    equipes = Equipe.objects.all()
    classement = sorted(equipes, key=lambda e: e.points, reverse=True)
    return render(request, 'tournoi/classement.html', {'equipes': equipes})

def stats_tournoi(request):
    equipes = Equipe.objects.all()
    joueurs = Joueur.objects.all()

    meilleur_buteur = max(joueurs, key=lambda j: j.buts)
    plus_cartons = max(joueurs, key=lambda j: j.cartons_jaunes + j.cartons_rouges)
    meilleure_equipe = max(equipes, key=lambda e: sum(j.buts for j in e.joueurs.all()))
    pire_equipe = max(equipes, key=lambda e: sum(j.cartons_rouges + j.cartons_jaunes for j in e.joueurs.all()))

    context = {
        'meilleur_buteur': meilleur_buteur,
        'plus_cartons': plus_cartons,
        'meilleure_equipe': meilleure_equipe,
        'pire_equipe': pire_equipe,
        'equipes': equipes,
    }
    return render(request, 'tournoi/stats_tournoi.html', context)

def stats_equipes(request):
    equipes = Equipe.objects.all()

    meilleure_attaque = max(equipes, key=lambda e: e.buts_marques)
    pire_defense = max(equipes, key=lambda e: e.buts_encaisse)
    meilleure_forme = max(equipes, key=lambda e: e.points)

    return render(request, "tournoi/stats_equipes.html", {
        "meilleure_attaque": meilleure_attaque,
        "pire_defense": pire_defense,
        "meilleure_forme": meilleure_forme
    })

def stats_joueurs(request):
    joueurs = Joueur.objects.all()

    buteurs = sorted(joueurs, key=lambda j: j.buts, reverse=True)
    cartons = sorted(joueurs, key=lambda j: j.cartons_jaunes + j.cartons_rouges, reverse=True)
    suspendus = Joueur.objects.filter(suspendu=True)

    return render(request, "tournoi/stats_joueurs.html", {
        "buteurs": buteurs,
        "cartons": cartons,
        "suspendus": suspendus
    })

def stats_joueurs(request):
    meilleurs_buteurs = (
        Joueur.objects
        .annotate(nb_buts=Count('but'))
        .order_by('-nb_buts')
    )

    return render(request, 'tournoi/stats_joueurs.html', {
        'meilleurs_buteurs': meilleurs_buteurs
    })



def calendrier(request):
    matchs = Match.objects.all().order_by("date")
    return render(request, "matchs/calendrier.html", {
        "matchs": matchs
    })

def infos(request):
    sanctions = Joueur.objects.filter(suspendu=True)
    prochain_match = Match.objects.order_by("date").first()
    pv = PvCommission.objects.last()

    return render(request, "tournoi/infos.html", {
        "sanctions": sanctions,
        "prochain_match": prochain_match,
        "pv": pv
    })
    
def reclamation(request):
    if request.method == "POST":
        Reclamation.objects.create(
            equipe=request.user.equipe,
            titre=request.POST["titre"],
            message=request.POST["message"]
        )

    reclamations = Reclamation.objects.filter(equipe=request.user.equipe)
    return render(request, "tournoi/reclamations.html", {
        "reclamations": reclamations
    })


# app_tournoi/views.py
def resultats(request):
    # DEBUG — à supprimer après vérification
    print(">>> Tous les matchs:", list(Match.objects.values('id', 'equipe1__nom', 'equipe2__nom', 'statut', 'score1', 'score2')))
    
    matchs_a_venir = Match.objects.filter(statut='A_VENIR').order_by('date')
    matchs_joues = Match.objects.filter(statut='TERMINE').order_by('-date')
    
    print(">>> Matchs terminés:", matchs_joues.count())
    print(">>> Matchs à venir:", matchs_a_venir.count())
    
    context = {
        'matchs_a_venir': matchs_a_venir,
        'matchs_joues': matchs_joues,
        'nb_matchs': matchs_joues.count(),
    }
    return render(request, 'tournoi/resultats.html', context)

# app_tournoi/views.py

def galeries(request):
    # On récupère toutes les images de la galerie
    images = Galerie.objects.all().order_by('-date_ajout')  # ou selon ton modèle
    return render(request, 'tournoi/galeries.html', {
        'images': images
    })



def dashboard(request):
    equipes = list(Equipe.objects.all())
    matchs = Match.objects.order_by('date')

    maintenant = timezone.now()
    prochain_match = Match.objects.filter(date__gte=maintenant).order_by('date').first()

    today = timezone.localdate()
    match_du_jour = Match.objects.filter(date__date=today).first()

    premier_match_joue = Match.objects.filter(statut='joue').exists()

    classement_data = []
    for e in equipes:
        if not premier_match_joue:
            classement_data.append({
                'equipe': e, 'MJ': 0, 'V': 0, 'N': 0, 'D': 0,
                'BP': 0, 'BC': 0, 'Diff': 0, 'Pts': 0,
            })
        else:
            MJ = e.matchs1.filter(statut='joue').count() + e.matchs2.filter(statut='joue').count()
            BP = e.buts_marques_total
            BC = e.buts_encaisses_total
            Diff = BP - BC

            V = N = D = 0
            for m in e.matchs1.filter(statut='joue'):
                if m.score1 > m.score2: V += 1
                elif m.score1 == m.score2: N += 1
                else: D += 1
            for m in e.matchs2.filter(statut='joue'):
                if m.score2 > m.score1: V += 1
                elif m.score2 == m.score1: N += 1
                else: D += 1

            Pts = e.points
            classement_data.append({
                'equipe': e, 'MJ': MJ, 'V': V, 'N': N, 'D': D,
                'BP': BP, 'BC': BC, 'Diff': Diff, 'Pts': Pts,
            })

    classement_data.sort(key=lambda x: (x['Pts'], x['Diff'], x['BP']), reverse=True)

    # Calcul des stats en Python car order_by ne fonctionne pas sur les propriétés
    if premier_match_joue:
        equipe_en_danger = max(equipes, key=lambda e: e.buts_encaisses_total) if equipes else None
        equipe_en_forme = max(equipes, key=lambda e: e.points) if equipes else None
        meilleure_attaque = max(equipes, key=lambda e: e.buts_marques_total) if equipes else None
        pire_defense = max(equipes, key=lambda e: e.buts_encaisses_total) if equipes else None
    else:
        equipe_en_danger = None
        equipe_en_forme = None
        meilleure_attaque = None
        pire_defense = None

    meilleur_buteur = (
        Joueur.objects
        .annotate(nb_buts=Count('but'))
        .order_by('-nb_buts')
        .first()
    )

    context = {
        "equipes": classement_data,
        "matchs": matchs,
        "prochain_match": prochain_match,
        "match_du_jour": match_du_jour,
        "equipe_en_danger": equipe_en_danger,
        "equipe_en_forme": equipe_en_forme,
        "meilleure_attaque": meilleure_attaque,
        "pire_defense": pire_defense,
        "meilleur_buteur": meilleur_buteur,
        "premier_match_joue": premier_match_joue,
    }

    return render(request, "tournoi/dashboard.html", context)

def admin_only(user):
    return user.is_staff

@user_passes_test(admin_only)
def admin_dashboard(request):
    matchs = Match.objects.all()
    equipes = Equipe.objects.all()
   

    return render(request, "tournoi/admin_dashboard.html", {
        "matchs": matchs,
        "equipes": equipes,
        "joueurs": joueurs,
    })    

@user_passes_test(admin_only)
def admin_matchs(request):
    matchs = Match.objects.all().order_by('-date')

    # Calcul du statut automatiquement
    maintenant = timezone.now()

    for m in matchs:
        if m.date > maintenant and (m.score_a is None and m.score_b is None):
            m.statut = "À venir"
        elif m.score_a is not None and m.score_b is not None:
            m.statut = "Terminé"
        else:
            m.statut = "En cours"

    return render(request, "tournoi/admin_matchs.html", {
        "matchs": matchs
    })

@user_passes_test(admin_only)
def admin_match_detail(request, id):
    match = get_object_or_404(Match, id=id)
    evenements = match.evenements.all()
    joueurs = Joueur.objects.filter(equipe__in=[match.equipe_a, match.equipe_b])

    if request.method == "POST":
        # Mise à jour score
        match.score_a = request.POST.get("score_a")
        match.score_b = request.POST.get("score_b")
        match.statut = request.POST.get("statut")
        match.save()

        # Ajout événement
        if request.POST.get("joueur"):
            EvenementMatch.objects.create(
                match=match,
                joueur_id=request.POST.get("joueur"),
                type_evenement=request.POST.get("type_evenement"),
                minute=request.POST.get("minute")
            )

        return redirect("admin_match_detail", id=match.id)

    return render(request, "tournoi/admin_match_detail.html", {
        "match": match,
        "evenements": evenements,
        "joueurs": joueurs,
    })   

def admin_only(user):
    return user.is_staff

@user_passes_test(admin_only)
def admin_equipes(request):
    equipes = Equipe.objects.all()

    return render(request, "tournoi/admin_equipes.html", {
        "equipes": equipes
    })

def admin_only(user):
    return user.is_staff

@user_passes_test(admin_only)
def admin_joueurs(request, equipe_id):
    # Récupérer l'équipe
    equipe = get_object_or_404(Equipe, id=equipe_id)
    # Récupérer les joueurs de cette équipe
    joueurs = Joueur.objects.filter(equipe=equipe)
    
    return render(request, "tournoi/admin_joueurs.html", {
        "equipe": equipe,
        "joueurs": joueurs,
    })         