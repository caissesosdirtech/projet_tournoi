from django.shortcuts import render

def discipline(request):

    joueurs = Joueur.objects.all()

    data = []

    for j in joueurs:
        jaunes = Evenement.objects.filter(joueur=j, type_evenement="carton_jaune").count()
        rouges = Evenement.objects.filter(joueur=j, type_evenement="carton_rouge").count()

        suspension = Suspension.objects.filter(joueur=j, actif=True).first()

        data.append({
            'joueur': j,
            'jaunes': jaunes,
            'rouges': rouges,
            'suspension': suspension.matchs_restants if suspension else 0,
            'statut': "Suspendu" if suspension else "Disponible"
        })

    return render(request, "sanctions/discipline.html", {"data": data})