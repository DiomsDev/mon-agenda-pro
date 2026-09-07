from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Activite, RendezVous
from missions.models import Mission
from .forms import ActiviteForm, RendezVousForm
from missions.forms import MissionForm

import calendar
from historique.models import HistoriqueAction
from historique.utils import enregistrer_action

# =========================================================
# TABLEAU DE BORD
# =========================================================

@login_required
def dashboard(request):
    aujourdhui = timezone.localdate()

    activites_a_venir = Activite.objects.filter(
        date__gte=aujourdhui
    ).order_by("date", "heure_debut")

    activites_effectuees = Activite.objects.filter(
        statut="effectuee"
    ).order_by("-date")

    nombre_activites_a_venir = activites_a_venir.count()
    nombre_activites_effectuees = activites_effectuees.count()

    nombre_rendez_vous = RendezVous.objects.filter(
        statut__in=["planifie", "confirme"]
    ).count()

    nombre_missions = Mission.objects.exclude(
        statut__in=["terminee", "annulee"]
    ).count()

    context = {
        "activites_a_venir": activites_a_venir,
        "activites_effectuees": activites_effectuees,
        "nombre_activites_a_venir": nombre_activites_a_venir,
        "nombre_activites_effectuees": nombre_activites_effectuees,
        "nombre_rendez_vous": nombre_rendez_vous,
        "nombre_missions": nombre_missions,
    }

    return render(request, "agenda/dashboard.html", context)


# =========================================================
# AGENDA
# =========================================================

@login_required
def agenda(request):
    aujourdhui = timezone.localdate()
    annee = int(request.GET.get("annee", aujourdhui.year))
    mois = int(request.GET.get("mois", aujourdhui.month))

    cal = calendar.Calendar(firstweekday=0)
    semaines = cal.monthdatescalendar(annee, mois)

    activites = Activite.objects.filter(date__year=annee, date__month=mois)
    rendez_vous = RendezVous.objects.filter(date__year=annee, date__month=mois)

    evenements_par_jour = {}
    for a in activites:
        evenements_par_jour.setdefault(a.date, []).append({"type": "activite", "objet": a})
    for r in rendez_vous:
        evenements_par_jour.setdefault(r.date, []).append({"type": "rendez_vous", "objet": r})

    semaines_avec_evenements = []
    for semaine in semaines:
        jours = []
        for jour in semaine:
            jours.append({
                "date": jour,
                "dans_le_mois": jour.month == mois,
                "aujourdhui": jour == aujourdhui,
                "evenements": evenements_par_jour.get(jour, []),
            })
        semaines_avec_evenements.append(jours)

    mois_precedent = mois - 1 if mois > 1 else 12
    annee_mois_precedent = annee if mois > 1 else annee - 1
    mois_suivant = mois + 1 if mois < 12 else 1
    annee_mois_suivant = annee if mois < 12 else annee + 1

    context = {
        "semaines": semaines_avec_evenements,
        "nom_mois": calendar.month_name[mois].capitalize(),
        "annee": annee,
        "mois_precedent": mois_precedent,
        "annee_mois_precedent": annee_mois_precedent,
        "mois_suivant": mois_suivant,
        "annee_mois_suivant": annee_mois_suivant,
    }
    return render(request, "agenda/agenda.html", context)


# =========================================================
# ACTIVITÉS
# =========================================================

@login_required
def activites(request):
    activites = Activite.objects.all().order_by("date", "heure_debut")
    return render(request, "agenda/activites.html", {"activites": activites})


# =========================================================
# MISSIONS
# =========================================================

@login_required
def missions(request):
    missions = Mission.objects.all().order_by("date_depart")
    return render(request, "agenda/missions.html", {"missions": missions})


# =========================================================
# RENDEZ-VOUS
# =========================================================

@login_required
def rendez_vous(request):
    rendez_vous = RendezVous.objects.all().order_by("date", "heure")
    return render(request, "agenda/rendez_vous.html", {"rendez_vous": rendez_vous})


# =========================================================
# RÉUNIONS / VISITEURS / CONTACTS / TÂCHES / RAPPELS /
# NOTIFICATIONS / COMPTES RENDUS / DOCUMENTS / STATISTIQUES
# (reportés à plus tard)
# =========================================================

@login_required
def reunions(request):
    return render(request, "agenda/reunions.html")


@login_required
def visiteurs(request):
    return render(request, "agenda/visiteurs.html")


@login_required
def contacts(request):
    return render(request, "agenda/contacts.html")


@login_required
def taches(request):
    return render(request, "agenda/taches.html")


@login_required
def rappels(request):
    return render(request, "agenda/rappels.html")


@login_required
def notifications(request):
    return render(request, "agenda/notifications.html")


@login_required
def comptes_rendus(request):
    return render(request, "agenda/comptes_rendus.html")


@login_required
def documents(request):
    return render(request, "agenda/documents.html")


@login_required
def statistiques(request):
    return render(request, "agenda/statistiques.html")


# =========================================================
# HISTORIQUE
# =========================================================

@login_required
def historique(request):
    actions = HistoriqueAction.objects.all().order_by("-date")

    # 🔎 Recherche
    recherche = request.GET.get("recherche", "").strip()

    if recherche:
        actions = actions.filter(
            utilisateur__username__icontains=recherche
        ) | actions.filter(
            action__icontains=recherche
        ) | actions.filter(
            description__icontains=recherche
        )

    # 🏷️ Filtre par type d'action
    type_action = request.GET.get("type_action", "").strip()

    if type_action:
        actions = actions.filter(action=type_action)

    # Limite à 200 actions
    actions = actions[:200]

    # Liste des types d'actions disponibles
    types_actions = (
        HistoriqueAction.objects
        .values_list("action", flat=True)
        .distinct()
        .order_by("action")
    )

    context = {
        "actions": actions,
        "recherche": recherche,
        "type_action": type_action,
        "types_actions": types_actions,
    }

    return render(request, "agenda/historique.html", context)


# =========================================================
# ASSISTANTS
# =========================================================

@login_required
def assistants(request):
    return render(request, "agenda/assistants.html")


# =========================================================
# PARAMÈTRES
# =========================================================

@login_required
def parametres(request):
    return render(request, "agenda/parametres.html")


# =========================================================
# ACTIVITÉS — CRUD
# =========================================================

@login_required
def nouvelle_activite(request):
    if request.method == "POST":
        form = ActiviteForm(request.POST)
        if form.is_valid():
            activite = form.save(commit=False)
            activite.cree_par = request.user
            activite.save()
            enregistrer_action(request.user, "Création d'activité", f"Activité « {activite.objet} » créée")
            return redirect("activites")
    else:
        form = ActiviteForm()

    return render(request, "agenda/nouvelle_activite.html", {"form": form})


@login_required
def modifier_activite(request, pk):
    activite = get_object_or_404(Activite, pk=pk)

    if request.method == "POST":
        form = ActiviteForm(request.POST, instance=activite)
        if form.is_valid():
            form.save()
            enregistrer_action(request.user, "Modification d'activité", f"Activité « {activite.objet} » modifiée")
            return redirect("activites")
    else:
        form = ActiviteForm(instance=activite)

    return render(request, "agenda/nouvelle_activite.html", {"form": form, "modification": True})


@login_required
def supprimer_activite(request, pk):
    activite = get_object_or_404(Activite, pk=pk)

    if request.method == "POST":
        objet = activite.objet
        activite.delete()
        enregistrer_action(request.user, "Suppression d'activité", f"Activité « {objet} » supprimée")
        return redirect("activites")

    return render(request, "agenda/supprimer_activite.html", {"activite": activite})


# =========================================================
# MISSIONS — CRUD
# =========================================================

@login_required
def nouvelle_mission(request):
    if request.method == "POST":
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.cree_par = request.user
            mission.save()
            enregistrer_action(request.user, "Création de mission", f"Mission « {mission.motif} » créée")
            return redirect("missions")
    else:
        form = MissionForm()

    return render(request, "agenda/nouvelle_mission.html", {"form": form})


@login_required
def modifier_mission(request, pk):
    mission = get_object_or_404(Mission, pk=pk)

    if request.method == "POST":
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            enregistrer_action(request.user, "Modification de mission", f"Mission « {mission.motif} » modifiée")
            return redirect("missions")
    else:
        form = MissionForm(instance=mission)

    return render(request, "agenda/nouvelle_mission.html", {"form": form, "modification": True})


@login_required
def supprimer_mission(request, pk):
    mission = get_object_or_404(Mission, pk=pk)

    if request.method == "POST":
        motif = mission.motif
        mission.delete()
        enregistrer_action(request.user, "Suppression de mission", f"Mission « {motif} » supprimée")
        return redirect("missions")

    return render(request, "agenda/supprimer_mission.html", {"mission": mission})


# =========================================================
# RENDEZ-VOUS — CRUD
# =========================================================

@login_required
def nouveau_rendez_vous(request):
    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.cree_par = request.user
            rdv.save()
            enregistrer_action(request.user, "Création de rendez-vous", f"Rendez-vous « {rdv.objet} » créé")
            return redirect("rendez_vous")
    else:
        form = RendezVousForm()

    return render(request, "agenda/nouveau_rendez_vous.html", {"form": form})


@login_required
def modifier_rendez_vous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)

    if request.method == "POST":
        form = RendezVousForm(request.POST, instance=rdv)
        if form.is_valid():
            form.save()
            enregistrer_action(request.user, "Modification de rendez-vous", f"Rendez-vous « {rdv.objet} » modifié")
            return redirect("rendez_vous")
    else:
        form = RendezVousForm(instance=rdv)

    return render(request, "agenda/nouveau_rendez_vous.html", {"form": form, "modification": True})


@login_required
def supprimer_rendez_vous(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)

    if request.method == "POST":
        objet = rdv.objet
        rdv.delete()
        enregistrer_action(request.user, "Suppression de rendez-vous", f"Rendez-vous « {objet} » supprimé")
        return redirect("rendez_vous")

    return render(request, "agenda/supprimer_rendez_vous.html", {"rendez_vous": rdv})