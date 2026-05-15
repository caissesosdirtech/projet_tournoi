from django.contrib.admin.views.decorators import staff_member_required
from .models import Reclamation
from .forms import ReclamationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_protect
from .forms import DecisionReclamationForm
from reclamations.models import Reclamation
from django.shortcuts import get_object_or_404



@login_required
def liste_reclamations(request):

    reclamations = Reclamation.objects.all().order_by("-date")

    return render(request,
    "reclamations/liste_reclamations.html",
    {"reclamations":reclamations})

    

@login_required(login_url='login_reclamation')
def creer_reclamation(request):

    # Vérifier si l'utilisateur est Capitaine ou Coach
    if not request.user.groups.filter(name__in=['Capitaine', 'Coach']).exists():
        messages.error(request, "❌ Seuls les capitaines ou coachs peuvent envoyer une réclamation.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ReclamationForm(request.POST, request.FILES)

        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.auteur = request.user
            reclamation.save()

            messages.success(request, "✅ Réclamation envoyée avec succès.")
            return redirect('dashboard')

    else:
        form = ReclamationForm()

    return render(request, 'reclamations/creer_reclamation.html', {
        'form': form
    })

@csrf_protect
def login_reclamation(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:

            # Vérifier si Capitaine ou Coach
            if user.groups.filter(name__in=['Capitaine','Coach']).exists():

                login(request, user)
                return redirect('creer_reclamation')

            # Admin
            elif user.is_staff:

                login(request, user)
                return redirect('admin_dashboard')

            else:
                messages.error(request,"⛔ Accès réservé aux capitaines et coachs")

        else:
            messages.error(request,"❌ Identifiants incorrects")

    return render(request,"reclamations/login_reclamation.html")


def reclamation(request):

    equipes = Equipe.objects.all()
    reclamations_en_attente = Reclamation.objects.filter(statut="attente").count()

    context = {
        'equipes': equipes,
        'reclamations_en_attente': reclamations_en_attente,
    }

    return render(request, 'reclamations/reclamation.html', context)


@login_required
def decision_reclamation(request, id):
    reclamation = Reclamation.objects.get(id=id)

    if request.method == "POST":
        form = DecisionReclamationForm(request.POST, request.FILES, instance=reclamation)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Réclamation traitée avec succès.")
            return redirect("liste_reclamations")
    else:
        form = DecisionReclamationForm(instance=reclamation)

    return render(request, "reclamations/decision_reclamation.html", {
        "form": form,
        "reclamation": reclamation
    }) 


@login_required
def supprimer_reclamation(request, id):
    reclamation = get_object_or_404(Reclamation, id=id)

    if request.method == "POST":
        reclamation.delete()
        messages.success(request, "🗑 Recours supprimée avec succès.")
        return redirect('liste_reclamations')

    return redirect('liste_reclamations')      