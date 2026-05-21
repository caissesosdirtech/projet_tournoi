from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required

from .models import Reclamation, ReclamationCommentaire
from .forms import (
    ReclamationForm,
    DecisionReclamationForm,
    CommentaireForm
)

from app_tournoi.models import Equipe


# =========================================================
# 🔐 LOGIN RECOURS
# =========================================================
def login_reclamation(request):

    next_url = request.GET.get("next")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # ❌ utilisateur introuvable
        if user is None:

            messages.error(
                request,
                "❌ Identifiants incorrects"
            )

            return render(
                request,
                "reclamations/login_reclamation.html"
            )

        # ❌ sécurité groupes
        if not user.groups.filter(
            name__in=["Capitaines", "Coachs"]
        ).exists():

            messages.error(
                request,
                "⛔ Accès réservé aux capitaines et coachs"
            )

            return render(
                request,
                "reclamations/login_reclamation.html"
            )

        # ✅ connexion
        login(request, user)

        # 🔁 redirection intelligente
        if next_url == "mes_reclamations":
            return redirect("mes_reclamations")

        return redirect("recours_dashboard")

    return render(
        request,
        "reclamations/login_reclamation.html"
    )


# =========================================================
# 📌 DASHBOARD UNIQUE RECOURS
# =========================================================
@login_required(login_url='login_reclamation')
def recours_dashboard(request):

    # 🔐 sécurité
    if not request.user.groups.filter(
        name__in=['Capitaines', 'Coachs']
    ).exists():

        messages.error(
            request,
            "⛔ Accès réservé aux capitaines et coachs."
        )

        return redirect('login_reclamation')

    # ==========================
    # FORMULAIRE
    # ==========================
    form = ReclamationForm(
        request.POST or None,
        request.FILES or None
    )

    # ==========================
    # ENVOI RECOURS
    # ==========================
    if request.method == "POST":

        if form.is_valid():

            rec = form.save(commit=False)

            rec.utilisateur = request.user

            # statut par défaut
            rec.statut = "en_attente"

            rec.save()

            messages.success(
                request,
                "✅ Votre recours a été envoyé avec succès."
            )

            return redirect('recours_dashboard')

        else:

            print(form.errors)

            messages.error(
                request,
                "❌ Veuillez corriger les erreurs."
            )

    # ==========================
    # MES RECOURS
    # ==========================
    reclamations = Reclamation.objects.filter(
        utilisateur=request.user
    ).order_by('-date')

    return render(
        request,
        "reclamations/recours_dashboard.html",
        {
            "form": form,
            "reclamations": reclamations
        }
    )


# =========================================================
# 📊 SUIVRE MES RECOURS
# =========================================================
@login_required(login_url='login_reclamation')
def mes_reclamations(request):

    # 🔐 sécurité groupes
    if not request.user.groups.filter(
        name__in=['Capitaines', 'Coachs']
    ).exists():

        return redirect('login_reclamation')

    reclamations = Reclamation.objects.filter(
        utilisateur=request.user
    ).order_by('-date')

    return render(
        request,
        "reclamations/mes_reclamations.html",
        {
            "reclamations": reclamations
        }
    )


# =========================================================
# 📩 CREER RECLAMATION
# =========================================================
@login_required(login_url='login_reclamation')
def creer_reclamation(request):

    # 🔐 sécurité groupes
    if not request.user.groups.filter(
        name__in=['Capitaines', 'Coachs']
    ).exists():

        return redirect('login_reclamation')

    form = ReclamationForm(
        request.POST or None,
        request.FILES or None
    )

    if request.method == "POST":

        if form.is_valid():

            rec = form.save(commit=False)

            rec.utilisateur = request.user

            rec.statut = "en_attente"

            rec.save()

            messages.success(
                request,
                "✅ Recours envoyé avec succès."
            )

            return redirect('dashboard')

        else:

            print(form.errors)

            messages.error(
                request,
                "❌ Veuillez corriger les erreurs."
            )

    return render(
        request,
        "reclamations/creer_reclamation.html",
        {
            "form": form
        }
    )


# =========================================================
# 👮 ADMIN : LISTE RECLAMATIONS
# =========================================================
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

@staff_member_required
def liste_reclamations(request):

    reclamations = Reclamation.objects.all().order_by("-date")

    reclamations_en_attente = reclamations.filter(
        statut='en_attente'
    ).count()

    reclamations_en_cours = reclamations.filter(
        statut='en_cours'
    ).count()

    reclamations_traitees = reclamations.filter(
        statut='traitee'
    ).count()

    context = {
        'reclamations': reclamations,
        'reclamations_en_attente': reclamations_en_attente,
        'reclamations_en_cours': reclamations_en_cours,
        'reclamations_traitees': reclamations_traitees,
        'page': 'liste_reclamations',
    }

    return render(
        request,
        "matchs/admin_dashboard.html",
        context
    )


# =========================================================
# 👮 TRAITEMENT RECLAMATION
# =========================================================
@staff_member_required
def decision_reclamation(request, id):

    # récupérer la réclamation
    reclamation = get_object_or_404(
        Reclamation,
        id=id
    )

    # formulaire
    form = DecisionReclamationForm(
        request.POST or None,
        request.FILES or None,
        instance=reclamation
    )

    # =====================================================
    # ENREGISTREMENT
    # =====================================================
    if request.method == "POST":

        if form.is_valid():

            rec = form.save(commit=False)

            # =============================================
            # GESTION AUTOMATIQUE STATUT
            # =============================================
            if rec.decision_commission == "accepte":

                rec.statut = "traitee"

            elif rec.decision_commission == "rejete":

                rec.statut = "rejetee"

            elif rec.decision_commission == "partiel":

                rec.statut = "en_cours"

            else:

                rec.statut = "en_attente"

            # sauvegarde
            rec.save()

            messages.success(
                request,
                "✅ Décision enregistrée avec succès."
            )

            return redirect("liste_reclamations")

        else:

            print(form.errors)

            messages.error(
                request,
                "❌ Erreur dans le formulaire."
            )

    # =====================================================
    # AFFICHAGE PAGE
    # =====================================================
    return render(
        request,
        "reclamations/decision_reclamation.html",
        {
            "form": form,
            "reclamation": reclamation
        }
    )

# =========================================================
# 💬 COMMENTAIRES
# =========================================================
@login_required
def ajouter_commentaire(request, id):

    reclamation = get_object_or_404(
        Reclamation,
        id=id
    )

    form = CommentaireForm(
        request.POST or None
    )

    if request.method == "POST":

        if form.is_valid():

            commentaire = form.save(commit=False)

            commentaire.reclamation = reclamation
            commentaire.utilisateur = request.user

            commentaire.save()

            messages.success(
                request,
                "💬 Commentaire ajouté."
            )

            return redirect('mes_reclamations')

    return render(
        request,
        "reclamations/commentaire.html",
        {
            "form": form,
            "reclamation": reclamation
        }
    )


# =========================================================
# 🗑 SUPPRESSION ADMIN
# =========================================================
@staff_member_required
def supprimer_reclamation(request, id):

    reclamation = get_object_or_404(
        Reclamation,
        id=id
    )

    if request.method == "POST":

        reclamation.delete()

        messages.success(
            request,
            "🗑 Réclamation supprimée avec succès."
        )

    return redirect('liste_reclamations')


# =========================================================
# 📄 PAGE GENERALE RECOURS
# =========================================================
def reclamation(request):

    equipes = Equipe.objects.all()

    reclamations_en_attente = Reclamation.objects.filter(
        statut="en_attente"
    ).count()

    context = {
        'equipes': equipes,
        'reclamations_en_attente': reclamations_en_attente,
    }

    return render(
        request,
        'reclamations/reclamation.html',
        context
    )