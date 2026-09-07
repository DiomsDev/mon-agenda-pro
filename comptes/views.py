from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import InscriptionForm
from .models import Utilisateur
from .forms import ProfilForm

def inscription(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Compte créé avec succès. Il doit maintenant être activé avant de pouvoir vous connecter."
            )
            return redirect("login")
    else:
        form = InscriptionForm()
    return render(request, "comptes/inscription.html", {"form": form})


@login_required
def gestion_acces(request):
    if request.user.role != "directeur":
        raise PermissionDenied

    mes_assistants = Utilisateur.objects.filter(directeur=request.user)
    assistants_disponibles = Utilisateur.objects.filter(role="assistant", directeur__isnull=True)

    context = {
        "mes_assistants": mes_assistants,
        "assistants_disponibles": assistants_disponibles,
    }
    return render(request, "comptes/gestion_acces.html", context)


@login_required
def rattacher_assistant(request, pk):
    if request.user.role != "directeur":
        raise PermissionDenied

    assistant = get_object_or_404(Utilisateur, pk=pk, role="assistant")
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