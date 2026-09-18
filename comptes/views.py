from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import InscriptionForm
from .models import Utilisateur
from .forms import ProfilForm

from .forms import CreerEntrepriseForm, RejoindreEntrepriseForm


def inscription(request):
    return render(request, "comptes/inscription_choix.html")


def creer_entreprise(request):
    if request.method == "POST":
        form = CreerEntrepriseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Votre entreprise a été créée avec succès. Vous pouvez vous connecter dès maintenant."
            )
            return redirect("login")
    else:
        form = CreerEntrepriseForm()
    return render(request, "comptes/creer_entreprise.html", {"form": form})


def rejoindre_entreprise(request):
    if request.method == "POST":
        form = RejoindreEntrepriseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Compte créé avec succès. Il doit maintenant être activé par votre directeur avant de pouvoir vous connecter."
            )
            return redirect("login")
    else:
        form = RejoindreEntrepriseForm()
    return render(request, "comptes/rejoindre_entreprise.html", {"form": form})




@login_required
def gestion_acces(request):
    if request.user.role != "directeur":
        raise PermissionDenied

    entreprise = request.user.entreprise

    mes_assistants = Utilisateur.objects.filter(directeur=request.user, entreprise=entreprise)
    assistants_disponibles = Utilisateur.objects.filter(
        role="assistant", directeur__isnull=True, entreprise=entreprise
    )

    context = {
        "mes_assistants": mes_assistants,
        "assistants_disponibles": assistants_disponibles,
    }
    return render(request, "comptes/gestion_acces.html", context)





@login_required
def rattacher_assistant(request, pk):
    if request.user.role != "directeur":
        raise PermissionDenied

    assistant = get_object_or_404(
        Utilisateur, pk=pk, role="assistant", entreprise=request.user.entreprise
    )
    assistant.directeur = request.user
    assistant.statut_acces = "actif"
    assistant.save()
    return redirect("gestion_acces")





@login_required
def basculer_acces(request, pk):
    if request.user.role != "directeur":
        raise PermissionDenied

    assistant = get_object_or_404(Utilisateur, pk=pk, directeur=request.user)
    assistant.statut_acces = "inactif" if assistant.statut_acces == "actif" else "actif"
    assistant.save()
    return redirect("gestion_acces")






@login_required
def modifier_profil(request):
    if request.method == "POST":
        form = ProfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect("parametres")
    else:
        form = ProfilForm(instance=request.user)

    return render(request, "comptes/modifier_profil.html", {"form": form})



