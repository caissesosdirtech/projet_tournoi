# ================= IMPORTS PYTHON =================
from datetime import date, datetime

# ================= IMPORTS DJANGO =================
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.db.models import Q, F, Sum, Count
from django.db import IntegrityError
from .models import Joueur
from django.core.paginator import Paginator
from django.shortcuts import render

# ================= MODELS =================
from equipes.models import Equipe
from joueurs.models import Joueur
from reclamations.models import Reclamation
from matchs.models import Match, Evenement, But, Carton, InfoTournoi, Notification, Galerie
from sanctions.models import Suspension

# ================= FORMS =================
from .forms import InfoTournoiForm

# ================= UTILS =================
from .utils import get_equipes
from django.http import HttpResponse


def dashboard(request):

    # ================== MATCHS ==================
    prochain_match = Match.objects.filter(date__gt=date.today()).order_by('date').first()
    match_du_jour = Match.objects.filter(date__date=date.today()).first()

    # Limiter à 3 prochains matchs déjà programmés
    prochains_matchs = Match.objects.filter(date__gt=date.today()).order_by('date')[:3]

    equipes = list(Equipe.objects.all())
    premier_match_joue = Match.objects.filter(score1__isnull=False).exists()

    # ================== CLASSEMENT ==================
    classement_data = []

    for e in equipes:
        if not premier_match_joue:
            classement_data.append({
                'equipe': e,
                'MJ': 0,
                'V': 0,
                'N': 0,
                'D': 0,
                'BP': 0,
                'BC': 0,
                'Diff': 0,
                'Pts': 0,
            })
        else:
            MJ = e.matchs1.filter(score1__isnull=False).count() + e.matchs2.filter(score1__isnull=False).count()
            BP = e.buts_marques_total
            BC = e.buts_encaisses_total
            Diff = BP - BC

            V = N = D = 0
            # matchs à domicile
            for m in e.matchs1.filter(score1__isnull=False):
                s1 = m.score1 or 0
                s2 = m.score2 or 0
                if s1 > s2:
                    V += 1
                elif s1 == s2:
                    N += 1
                else:
                    D += 1
            # matchs à l'extérieur
            for m in e.matchs2.filter(score1__isnull=False):
                s1 = m.score1 or 0
                s2 = m.score2 or 0
                if s2 > s1:
                    V += 1
                elif s2 == s1:
                    N += 1
                else:
                    D += 1

            Pts = V * 3 + N

            classement_data.append({
                'equipe': e,
                'MJ': MJ,
                'V': V,
                'N': N,
                'D': D,
                'BP': BP,
                'BC': BC,
                'Diff': Diff,
                'Pts': Pts,
            })

    # tri du classement
    classement_data.sort(key=lambda x: (x['Pts'], x['Diff'], x['BP']), reverse=True)

    # ================== STATS JOUEURS ==================
    meilleurs_buteurs = Joueur.objects.annotate(
        nb_buts=Count('buts')
    ).filter(nb_buts__gt=0).order_by('-nb_buts')[:3]  # <- Limite à 3
    meilleur_buteur = meilleurs_buteurs.first()

    # ================== STATS EQUIPES ==================
    meilleure_attaque = max(classement_data, key=lambda x: x['BP'])['equipe'] if classement_data else None
    pire_defense = max(classement_data, key=lambda x: x['BC'])['equipe'] if classement_data else None
    equipe_en_forme = classement_data[0]['equipe'] if classement_data else None
    equipe_en_danger = classement_data[-1]['equipe'] if classement_data else None

    # ================== RECLAMATIONS TRAITEES ==================
    notifications_reclamations = Reclamation.objects.filter(
        statut='traitee',
        document_final__isnull=False
    ).order_by('-date')


    # ================== AJOUT INFOS ==================

    infos = InfoTournoi.objects.all().order_by('-id')

    notifications = Notification.objects.all().order_by('-date_creation')[:5]

    context = {
        # matchs
        'prochain_match': prochain_match,
        'match_du_jour': match_du_jour,
        'matchs': prochains_matchs,  # <- Utilisation des 3 prochains matchs

        # classement
        'classement': classement_data,
        'premier_match_joue': premier_match_joue,

        # stats joueurs
        'meilleurs_buteurs': meilleurs_buteurs,  # <- 3 meilleurs
        'meilleur_buteur': meilleur_buteur,

        # stats équipes
        'meilleure_attaque': meilleure_attaque,
        'pire_defense': pire_defense,
        'equipe_en_forme': equipe_en_forme,
        'equipe_en_danger': equipe_en_danger,

        # sidebar
        'equipes': Equipe.objects.all(),

        # notifications réclamations
        'notifications_reclamations': notifications_reclamations,

        # infos
        'infos' : infos,

        # notifications
        'notifications': notifications,
    }

    return render(request, 'matchs/dashboard.html', context)

    # ================== RECLAMATIONS TRAITEES ==================
    notifications_reclamations = Reclamation.objects.filter(
        statut='traitee',
        document_final__isnull=False
    ).order_by('-date')

    context = {
        # matchs
        'prochain_match': prochain_match,
        'match_du_jour': match_du_jour,
        'matchs': Match.objects.order_by('date')[:10],

        # classement
        'classement': classement_data,
        'premier_match_joue': premier_match_joue,

        # stats joueurs
        'meilleurs_buteurs': meilleurs_buteurs,
        'meilleur_buteur': meilleur_buteur,

        # stats équipes
        'meilleure_attaque': meilleure_attaque,
        'pire_defense': pire_defense,
        'equipe_en_forme': equipe_en_forme,
        'equipe_en_danger': equipe_en_danger,

        # sidebar
        'equipes': Equipe.objects.all(),

        # notifications réclamations
        'notifications_reclamations': notifications_reclamations,
    }

    return render(request, 'matchs/dashboard.html', context)


def calendrier(request):
    now = timezone.now()
    # Tri des matchs par date décroissante pour mettre le dernier en premier
    matchs = Match.objects.order_by('-date')  
    equipes = Equipe.objects.all()

    context = {
        'matchs': matchs,
        'equipes': equipes,
        'now': now,
    }

    return render(request, 'matchs/calendrier.html', context)

def classement(request):

    equipes = Equipe.objects.all()
    classement_data = []

    for e in equipes:

        matchs_joues = (
            e.matchs1.filter(score1__isnull=False, score2__isnull=False) |
            e.matchs2.filter(score1__isnull=False, score2__isnull=False)
        )

        MJ = matchs_joues.count()

        V = 0
        N = 0
        D = 0
        BP = 0
        BC = 0
        Pts = 0

        for m in matchs_joues:

            if m.equipe1 == e:
                buts_pour = m.score1
                buts_contre = m.score2
            else:
                buts_pour = m.score2
                buts_contre = m.score1

            BP += buts_pour
            BC += buts_contre

            if buts_pour > buts_contre:
                V += 1
                Pts += 3
            elif buts_pour == buts_contre:
                N += 1
                Pts += 1
            else:
                D += 1

        Diff = BP - BC

        classement_data.append({
            'equipe': e,
            'MJ': MJ,
            'V': V,
            'N': N,
            'D': D,
            'BP': BP,
            'BC': BC,
            'Diff': Diff,
            'Pts': Pts,
        })

    classement_data.sort(
        key=lambda x: (x['Pts'], x['Diff'], x['BP']),
        reverse=True
    )

    context = {
        'classement': classement_data,
        'equipes': equipes,
        'premier_match_joue': any(l['MJ'] > 0 for l in classement_data)
    }

    return render(request, 'matchs/classement.html', context)



def gerer_evenements(request, id):

    match = get_object_or_404(Match, id=id)

    # =========================
    # POST
    # =========================
    if request.method == "POST":

        type_evenement = request.POST.get('type_evenement')

    # 🔥 AJOUT ICI
        if match.statut == "termine" and type_evenement != "fin_match":
            return JsonResponse({
                "success": False,
                "message": "⛔ Match terminé. Aucun événement autorisé"
            })

        # =========================
        # ✅ FIN MATCH
        # =========================
        if type_evenement == "fin_match":

            match.score1 = match.score1 or 0
            match.score2 = match.score2 or 0
            match.statut = "termine"
            match.save()

            suspensions = Suspension.objects.filter(
                actif=True,
                joueur__equipe__in=[match.equipe1, match.equipe2]
            ).exclude(match_declencheur=match)

            for s in suspensions:
                s.matchs_restants -= 1
                if s.matchs_restants <= 0:
                    s.actif = False
                s.save()

            return JsonResponse({
                "success": True,
                "message": "Match terminé",
                "score1": match.score1,
                "score2": match.score2
            })

        joueur_id = request.POST.get('joueur')
        minute = request.POST.get('minute')

        if not joueur_id or not minute:
            return JsonResponse({
                "success": False,
                "message": "Champs manquants"
            })

        joueur = get_object_or_404(Joueur, id=joueur_id)

        # 🚫 joueur suspendu
        if Suspension.objects.filter(joueur=joueur, actif=True).exists():
            return JsonResponse({
                "success": False,
                "message": "⛔ Joueur suspendu"
            })

        # =========================
        # BUT
        # =========================
        if type_evenement == "but":

            Evenement.objects.create(
                match=match,
                joueur=joueur,
                type_evenement=type_evenement,
                minute=minute
            )

            But.objects.create(
                match=match,
                joueur=joueur,
                minute=minute
            )

            match.score1 = match.score1 or 0
            match.score2 = match.score2 or 0

            if joueur.equipe == match.equipe1:
                match.score1 += 1
            else:
                match.score2 += 1

            match.save()

        # =========================
        # CARTON JAUNE (gestion double jaune)
        # =========================
        elif type_evenement == "carton_jaune":

            nb_jaunes = Evenement.objects.filter(
                match=match,
                joueur=joueur,
                type_evenement="carton_jaune"
            ).count()

            # 👉 2ème jaune → rouge automatique
            if nb_jaunes >= 1:

                # ajouter jaune
                Evenement.objects.create(
                    match=match,
                    joueur=joueur,
                    type_evenement="carton_jaune",
                    minute=minute
                )

                # ajouter rouge automatique
                Evenement.objects.create(
                    match=match,
                    joueur=joueur,
                    type_evenement="carton_rouge",
                    minute=minute
                )

                # suspension
                Suspension.objects.create(
                    joueur=joueur,
                    matchs_restants=2,
                    actif=True,
                    match_declencheur=match
                )

                return JsonResponse({
                    "success": True,
                    "message": "🟥 Double jaune → suspension",
                    "type": "carton_rouge",
                    "joueur": f"{joueur.nom} {joueur.prenom}",
                    "minute": minute,
                    "equipe": joueur.equipe.id,
                    "score1": match.score1 or 0,
                    "score2": match.score2 or 0
                })

            else:
                # 1er jaune normal
                Evenement.objects.create(
                    match=match,
                    joueur=joueur,
                    type_evenement="carton_jaune",
                    minute=minute
                )

        # =========================
        # ROUGE DIRECT
        # =========================
        elif type_evenement == "carton_rouge":

            Evenement.objects.create(
                match=match,
                joueur=joueur,
                type_evenement="carton_rouge",
                minute=minute
            )

            Suspension.objects.create(
                joueur=joueur,
                matchs_restants=2,
                actif=True
            )

        # =========================
        # AUTRES EVENEMENTS
        # =========================
        else:
            Evenement.objects.create(
                match=match,
                joueur=joueur,
                type_evenement=type_evenement,
                minute=minute
            )

        return JsonResponse({
            "success": True,
            "message": "Événement ajouté",
            "type": type_evenement,
            "joueur": f"{joueur.nom} {joueur.prenom}",
            "minute": minute,
            "equipe": joueur.equipe.id,
            "score1": match.score1 or 0,
            "score2": match.score2 or 0
        })

    # =========================
    # ✅ GET
    # =========================
    joueurs = Joueur.objects.filter(
        equipe__in=[match.equipe1, match.equipe2]
    )

    for j in joueurs:
        susp = Suspension.objects.filter(joueur=j, actif=True).first()

        j.est_suspendu = True if susp else False
        j.matchs_restants = susp.matchs_restants if susp else 0    

    evenements = match.evenements.all().order_by('minute')

    return render(request, 'matchs/gerer_evenements.html', {
        'match': match,
        'joueurs': joueurs,
        'evenements': evenements
    })

# ----------------- Vue pour ajouter une info (via formulaire admin) -----------------
@staff_member_required
def ajouter_info(request):

    if request.method == "POST":

        titre = request.POST.get("titre")
        description = request.POST.get("description")
        niveau = request.POST.get("niveau")
        fichier = request.FILES.get("fichier")

        info = InfoTournoi.objects.create(
            titre=titre,
            contenu=description,
            priorite=niveau,
            fichier=fichier
        )

        # Création automatique d'une notification
        Notification.objects.create(
            titre=titre,
            message=description,
            type_notification="info"
        )

    return redirect('admin_dashboard')


def ajouter_info_ajax(request):

    if request.method == "POST":

        titre = request.POST.get("titre")
        description = request.POST.get("description")
        niveau = request.POST.get("niveau")
        fichier = request.FILES.get("fichier")

        info = InfoTournoi.objects.create(
            titre=titre,
            contenu=description,
            priorite=niveau,
            fichier=fichier
        )

        data = {
            'success': True,
            'titre': info.titre,
            'description': info.contenu,
            'niveau': info.priorite,
            'fichier_url': info.fichier.url if info.fichier else ''
        }

        return JsonResponse(data)

    return JsonResponse({'success': False})      

def infos(request):
    return render(request, "matchs/infos.html")

def stats_equipes(request):
    equipes = Equipe.objects.all()

    # Calcul des stats par équipe
    stats = []
    classement_general = []

    # Préparer le classement général
    for e in equipes:
        matches = Match.objects.filter(Q(equipe1=e) | Q(equipe2=e))
        MJ = matches.count()
        victoires = matches.filter(
            (Q(equipe1=e) & Q(score1__gt=F('score2'))) |
            (Q(equipe2=e) & Q(score2__gt=F('score1')))
        ).count()
        nuls = matches.filter(score1=F('score2')).count()
        defaites = MJ - victoires - nuls

        bp = matches.filter(equipe1=e).aggregate(total=Sum('score1'))['total'] or 0
        bp += matches.filter(equipe2=e).aggregate(total=Sum('score2'))['total'] or 0

        bc = matches.filter(equipe1=e).aggregate(total=Sum('score2'))['total'] or 0
        bc += matches.filter(equipe2=e).aggregate(total=Sum('score1'))['total'] or 0

        diff = bp - bc
        pts = victoires*3 + nuls

        # Meilleur buteur de l'équipe
        joueurs = e.joueurs.all()  # supposons que related_name='joueurs' dans Joueur.equipe
        meilleur_buteur = None
        max_buts = 0
        for j in joueurs:
            nb_buts = But.objects.filter(joueur=j).count()
            if nb_buts > max_buts:
                max_buts = nb_buts
                meilleur_buteur = j

        stats.append({
            'equipe': e,
            'matches': MJ,
            'victoires': victoires,
            'nuls': nuls,
            'defaites': defaites,
            'bp': bp,
            'bc': bc,
            'diff': diff,
            'pts': pts,
            'meilleur_buteur': meilleur_buteur,
            'mb_buts': max_buts,
        })

        classement_general.append({
            'equipe': e,
            'Pts': pts,
            'Diff': diff,
        })

    # Tri pour classement général
    classement_general.sort(key=lambda x: (x['Pts'], x['Diff']), reverse=True)

    # Ajouter le rang de chaque équipe
    for idx, c in enumerate(classement_general, start=1):
        c['rang'] = idx
        # Ajouter ce rang à l'équipe correspondante dans stats
        for s in stats:
            if s['equipe'] == c['equipe']:
                s['rang'] = idx

    return render(request, 'matchs/stats_equipes.html', {'stats': stats, 'classement': classement_general})

def stats_joueurs(request):
    joueurs = Joueur.objects.all()
    stats = []

    for j in joueurs:
        total_buts = j.buts.count()  # chaque But = 1 but
        stats.append({
            'joueur': j,
            'buts': total_buts,
            'matches': j.match_set.count() if hasattr(j, 'match_set') else 0,
        })

    # Trier par nombre de buts décroissant et garder les 10 meilleurs
    stats_sorted = sorted(stats, key=lambda x: x['buts'], reverse=True)[:10]

    context = {
        'stats': stats_sorted,
        'equipes': Equipe.objects.all()
    }

    return render(request, "matchs/stats_joueurs.html", context)


def resultats(request):
    matchs_a_venir = Match.objects.filter(statut='programme').order_by('date')
    matchs_joues = Match.objects.filter(statut='termine').order_by('-date')
    context = {
        'matchs_a_venir': matchs_a_venir,
        'matchs_joues': matchs_joues,
        'nb_matchs': matchs_joues.count(),
    }
    return render(request, 'tournoi/resultats.html', context)

def galeries(request):

    images = Galerie.objects.all()
    equipes = Equipe.objects.all()

    context = {
        'images': images,
        'equipes': equipes
    }

    return render(request, 'matchs/galeries.html', context)


# ================= AUTH ADMIN =================

def admin_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Identifiants incorrects")
    return render(request, 'matchs/admin_login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')
    

@staff_member_required
def admin_dashboard(request):

    now = timezone.now()

    # ===== MATCHS =====
    matchs = Match.objects.all()

    equipe_id = request.GET.get('equipe')
    if equipe_id:
        matchs = matchs.filter(Q(equipe1_id=equipe_id) | Q(equipe2_id=equipe_id))

    statut = request.GET.get('statut')
    if statut:
        if statut == 'a_venir':
            matchs = matchs.filter(score1__isnull=True, date__gt=now)
        elif statut == 'en_cours':
            matchs = matchs.filter(score1__isnull=True, date__lte=now)
        elif statut == 'termine':
            matchs = matchs.filter(score1__isnull=False)

    # ===== FORM INFO =====
    if request.method == 'POST':
        info_form = InfoTournoiForm(request.POST, request.FILES)
        if info_form.is_valid():
            info_form.save()
            messages.success(request, "✅ Information ajoutée avec succès !")
            return redirect('admin_dashboard')
    else:
        info_form = InfoTournoiForm()

    # ===== INFOS =====
    infos = InfoTournoi.objects.all().order_by('-id')

    # ===== MEDIAS =====
    medias = Galerie.objects.filter(archive=False)

    # ===== STATS =====
    total_matchs = Match.objects.count()
    matchs_termines = Match.objects.filter(score1__isnull=False).count()
    matchs_a_venir = Match.objects.filter(score1__isnull=True, date__gt=now).count()
    matchs_en_cours = Match.objects.filter(score1__isnull=True, date__lte=now).count()

    prochain_match = Match.objects.filter(
        score1__isnull=True,
        date__gt=now
    ).order_by('date').first()

    top_team = Equipe.objects.annotate(
        num_joueurs=Count('joueurs')
    ).order_by('-num_joueurs').first()

    meilleur_buteur = Joueur.objects.annotate(
        nb_buts=Count('buts')
    ).filter(nb_buts__gt=0).order_by('-nb_buts').first()

    # ===== RECLAMATIONS =====
    total_reclamations = Reclamation.objects.count()
    reclamations_en_attente = Reclamation.objects.filter(statut='en_attente').count()
    reclamations_en_cours = Reclamation.objects.filter(statut='en_cours').count()
    reclamations_traitees = Reclamation.objects.filter(statut='traitee').count()

    # ===== CONTEXT UNIQUE =====
    context = {
        'matchs': matchs,
        'equipes': Equipe.objects.all(),
        'joueurs': Joueur.objects.all(),
        'medias': medias,
        'page': 'dashboard',
        'now': now,
        'prochain_match': prochain_match,

        'total_matchs': total_matchs,
        'matchs_a_venir': matchs_a_venir,
        'matchs_en_cours': matchs_en_cours,
        'matchs_termines': matchs_termines,

        'top_team': top_team,
        'meilleur_buteur': meilleur_buteur,

        'total_reclamations': total_reclamations,
        'reclamations_en_attente': reclamations_en_attente,
        'reclamations_en_cours': reclamations_en_cours,
        'reclamations_traitees': reclamations_traitees,

        # 🔥 IMPORTANT
        'infos': infos,
        'info_form': info_form,
    }

    return render(request, 'matchs/admin_dashboard.html', context)
    # ================= GESTION MATCHS =================

@login_required
def programmer_match(request):

    equipes = Equipe.objects.all()

    if request.method == "POST":

        equipe1 = Equipe.objects.get(id=request.POST.get("equipe1"))
        equipe2 = Equipe.objects.get(id=request.POST.get("equipe2"))

        date_str = request.POST.get('date')

        date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        stade = request.POST.get("stade")

        Match.objects.create(
            equipe1=equipe1,
            equipe2=equipe2,
            date=date,
            stade=stade
        )

        return redirect("admin_dashboard")

    return render(request, "matchs/programmer_match.html", {
        "equipes": equipes
    })


# ================= GESTION EQUIPES =================

def ajouter_equipe(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        coach1 = request.POST.get('coach1')
        coach2 = request.POST.get('coach2')
        logo = request.FILES.get('logo')  # <- récupère le fichier uploadé

        # Crée l'équipe avec le logo
        Equipe.objects.create(
            nom=nom,
            coach1=coach1,
            coach2=coach2,
            logo=logo
        )

        return redirect('liste_equipes')

    return render(request, 'matchs/ajouter_equipe.html')

def editer_equipe(request, id):
    equipe = get_object_or_404(Equipe, id=id)
    if request.method == 'POST':
        equipe.nom = request.POST['nom']
        equipe.coach1 = request.POST['coach1']
        equipe.coach2 = request.POST['coach2']
        equipe.save()
        return redirect('liste_equipes')
    return render(request, 'matchs/editer_equipe.html', {'equipe': equipe})  

def supprimer_equipe(request, id):
    equipe = Equipe.objects.get(id=id)

    if request.method == "POST":
        equipe.delete()
        return redirect('liste_equipes')

    return render(request, "matchs/supprimer_equipe.html", {'equipe': equipe})     


def liste_equipes(request):
    query = request.GET.get('q', '')
    equipes = Equipe.objects.all()
    if query:
        equipes = equipes.filter(nom__icontains=query)
    return render(request, 'matchs/admin_dashboard.html', {
        'equipes': equipes,
        'joueurs': Joueur.objects.all(),
        'matchs': Match.objects.all(),
        'page': 'liste_equipes',
    })


# ================= GESTION JOUEURS =================

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import Joueur, Equipe

def ajouter_joueur(request):
    if request.method == "POST":
        equipe = get_object_or_404(Equipe, id=request.POST.get('equipe_id'))
        try:
            Joueur.objects.create(
                nom=request.POST.get('nom'),
                prenom=request.POST.get('prenom'),
                numero=int(request.POST.get('numero')),
                poste=request.POST.get('poste'),
                equipe=equipe
            )
            return JsonResponse({
                'status': 'success',           # ← clé attendue par le JS
                'message': '✅ Joueur ajouté avec succès !'
            })
        except IntegrityError:
            return JsonResponse({
                'status': 'error',             # ← clé attendue par le JS
                'message': '❌ Numéro déjà utilisé dans cette équipe'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'❌ Erreur : {str(e)}'
            }, status=500)
        
def liste_joueurs(request):

    equipe_id = request.GET.get('equipe')
    query = request.GET.get('q', '')

    joueurs = Joueur.objects.all()

    if equipe_id and equipe_id.isdigit():
        joueurs = joueurs.filter(equipe_id=int(equipe_id))

    if query:
        joueurs = joueurs.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query)
        )

    paginator = Paginator(joueurs, 10)
    page_number = request.GET.get('page')
    joueurs_page = paginator.get_page(page_number)

    for j in joueurs_page:
        j.suspension_active = Suspension.objects.filter(
            joueur=j,
            actif=True
        ).first()

    return render(request, 'matchs/admin_dashboard.html', {
        'page': 'liste_joueurs',   # ✅ TRÈS IMPORTANT
        'joueurs': joueurs_page,
        'equipes': Equipe.objects.all(),
        'equipe_id': equipe_id,
    })

def supprimer_joueur(request, id):
    joueur = Joueur.objects.get(id=id)

    if request.method == "POST":
        joueur.delete()
        return redirect('liste_joueurs')

    return render(request, "matchs/supprimer_joueur.html", {'joueur': joueur})


def editer_joueur(request, id):
    if request.method == "POST":

        joueur = get_object_or_404(Joueur, id=id)

        try:
            joueur.nom = request.POST.get('nom')
            joueur.prenom = request.POST.get('prenom')
            joueur.numero = int(request.POST.get('numero'))
            joueur.poste = request.POST.get('poste')

            # ✅ AJOUT IMPORTANT
            equipe_id = request.POST.get('equipe')
            if equipe_id:
                joueur.equipe_id = int(equipe_id)

            joueur.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Joueur modifié avec succès'
            })

        except IntegrityError:
            return JsonResponse({
                'status': 'error',
                'message': 'Numéro déjà utilisé'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

def supprimer_match(request, id):
    match = get_object_or_404(Match, id=id)
    match.delete()
    return redirect('admin_dashboard')


def detail_equipe(request, equipe_id):
    equipe = get_object_or_404(Equipe, id=equipe_id)

    # 🔥 paramètre GET
    show_all = request.GET.get('all')

    if show_all:
        joueurs = equipe.joueurs.all()
    else:
        joueurs = equipe.joueurs.all()[:10]

    # le reste ne change pas

    # Matchs joués par l'équipe
    matchs = Match.objects.filter(
        Q(equipe1=equipe) | Q(equipe2=equipe)
    ).order_by('-date')


    meilleurs_buteurs = Joueur.objects.filter(
        equipe=equipe
    ).annotate(
        nb_buts=Count('buts')
    ).order_by('-nb_buts')[:3]

    # Statistiques
    MJ = matchs.count()
    V = N = D = BP = BC = 0

    for m in matchs:
        s1 = m.score1 or 0
        s2 = m.score2 or 0
        if m.equipe1 == equipe:
            BP += s1
            BC += s2
            if s1 > s2: V += 1
            elif s1 == s2: N += 1
            else: D += 1
        else:
            BP += s2
            BC += s1
            if s2 > s1: V += 1
            elif s2 == s1: N += 1
            else: D += 1

    Diff = BP - BC
    Pts = V*3 + N  # 3 points victoire, 1 point nul

    # Stats pour le graphique
    graph_data = []
    for match in matchs.order_by('date'):
        if match.equipe1 == equipe:
            graph_data.append({'date': match.date.strftime("%Y-%m-%d"), 'buts': match.score1 or 0})
        else:
            graph_data.append({'date': match.date.strftime("%Y-%m-%d"), 'buts': match.score2 or 0})

    context = {
        'equipe': equipe,
        'joueurs': joueurs,
        'matchs': matchs,
        'MJ': MJ,
        'V': V,
        'N': N,
        'D': D,
        'BP': BP,
        'BC': BC,
        'Diff': Diff,
        'Pts': Pts,
        'graph_data': graph_data,
        'meilleurs_buteurs': meilleurs_buteurs,
    }
    return render(request, 'matchs/detail_equipe.html', context)
    

def equipes_menu(request):
    return {
        'equipes': Equipe.objects.all()
    }

       

def verifier_meilleur_buteur():

    meilleur = Joueur.objects.annotate(
        total_buts=Count('but')
    ).order_by('-total_buts').first()

    if meilleur:
        Notification.objects.create(
            titre="Nouveau meilleur buteur ⚽",
            message=f"{meilleur.nom} est maintenant meilleur buteur avec {meilleur.total_buts} buts.",
            type_notification="buteur"
        )   

def terminer_match(request, match_id):

    match = Match.objects.get(id=match_id)

    match.statut = "terminé"
    match.save()

    Notification.objects.create(
        titre="Match terminé 🏆",
        message=f"{match.equipe_a.nom} {match.score1} - {match.score2} {match.equipe_b.nom}",
        type_notification="fin"
    )

    return redirect('calendrier')      


def galeries(request):

    medias = Galerie.objects.filter(archive=False).order_by('-date_ajout')

    return render(request, "matchs/galeries.html", {
        "medias": medias
    })


def archiver_media(request, id):

    media = get_object_or_404(Galerie, id=id)

    media.archive = True
    media.save()

    return redirect("galeries")   
    
@login_required
def medias_archives(request):

    medias = Galerie.objects.filter(archive=True).order_by('-date_ajout')

    return render(request,"matchs/medias_archives.html",{
        "medias":medias
    })  

@login_required
def restaurer_media(request, id):

    media = Galerie.objects.get(id=id)

    media.archive = False
    media.save()

    return redirect("medias_archives")  

@login_required
def supprimer_definitif_media(request, id):

    media = Galerie.objects.get(id=id)

    media.delete()

    return redirect("medias_archives")        

def ajouter_media(request):

    if request.method == "POST":

        titre = request.POST.get("titre")
        type_media = request.POST.get("type_media")

        fichiers = request.FILES.getlist('medias')

        for fichier in fichiers:

            if type_media == "photo":

                Galerie.objects.create(
                    titre=titre,
                    type_media="photo",
                    image=fichier
                )

            else:

                Galerie.objects.create(
                    titre=titre,
                    type_media="video",
                    video=fichier
                )

        return redirect("admin_dashboard")

    return render(request,"matchs/ajouter_media.html")

@login_required
def supprimer_media(request):

    medias = Galerie.objects.filter(archive=False)

    if request.method == "POST":

        medias_ids = request.POST.getlist("medias")

        Galerie.objects.filter(id__in=medias_ids).update(archive=True)

        return redirect("supprimer_media")

    return render(request,"matchs/supprimer_media.html",{
        "medias":medias
    }) 

def reglement_interieur(request):
    return render(request, 'tournoi/reglement_interieur.html')


from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

def telecharger_pdf(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'reglement.pdf')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reglement_interieur.pdf"'
            return response

    return HttpResponse("Fichier introuvable", status=404)

    return HttpResponse("Fichier introuvable", status=404)

def telecharger_odf(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'reglement.odt')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.oasis.opendocument.text'
            )
            response['Content-Disposition'] = 'attachment; filename="reglement_interieur.odt"'
            return response

    return HttpResponse("Fichier introuvable", status=404)    


    

from django.http import HttpResponse
from docx import Document

from django.http import HttpResponse
from django.conf import settings
import os

def telecharger_word(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'reglement.docx')

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(
                f.read(),
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            response['Content-Disposition'] = 'attachment; filename="reglement_interieur.docx"'
            return response

    return HttpResponse("Fichier introuvable", status=404) 
