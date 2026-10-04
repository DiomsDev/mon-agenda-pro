from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse, JsonResponse

import json
from django.conf import settings

from .models import (
    Activite,
    RendezVous,
    Reunion,
    CompteRendu,
    Tache,
)

from .forms import (
    ActiviteForm,
    RendezVousForm,
    ReunionForm,
    CompteRenduForm,
    TacheForm,
)

from missions.models import Mission
from missions.forms import MissionForm

from historique.models import (
    HistoriqueAction,
    Notification,
    PushSubscription,
)

from historique.utils import (
    enregistrer_action,
    creer_notification,
    verifier_rappels,
)

from entreprises.models import Entreprise

from comptes.models import Utilisateur

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from docx import Document

import calendar
from datetime import timedelta


# =========================================================
# TABLEAU DE BORD
# =========================================================

@login_required
def dashboard(request):

    aujourd_hui = timezone.localdate()

    # =========================================================
    # ENTREPRISE DE L'UTILISATEUR CONNECTÉ
    # =========================================================

    entreprise = request.user.entreprise

    # =========================================================
    # ACTIVITÉS À VENIR
    # =========================================================

    activites_a_venir = Activite.objects.filter(
        entreprise=entreprise,
        date__gte=aujourd_hui
    )

    # =========================================================
    # ACTIVITÉS EFFECTUÉES
    # =========================================================

    activites_effectuees = Activite.objects.filter(
        entreprise=entreprise,
        statut="effectuee"
    )

    # =========================================================
    # RENDEZ-VOUS
    # =========================================================

    nombre_rendez_vous = RendezVous.objects.filter(
        entreprise=entreprise,
        statut__in=["planifie", "confirme"]
    ).count()

    # =========================================================
    # MISSIONS
    # =========================================================

    nombre_missions = Mission.objects.filter(
        entreprise=entreprise
    ).exclude(
        statut__in=["terminee", "annulee"]
    ).count()

    # =========================================================
    # RÉUNIONS À VENIR
    # =========================================================

    nombre_reunions = Reunion.objects.filter(
        entreprise=entreprise,
        date__gte=aujourd_hui
    ).exclude(
        statut="annulee"
    ).count()

    # =========================================================
    # COMPTES RENDUS
    # =========================================================

    nombre_comptes_rendus = CompteRendu.objects.filter(
        entreprise=entreprise
    ).count()

    # =========================================================
    # STATISTIQUES
    # =========================================================

    annee_courante = aujourd_hui.year

    debut_semaine = (
        aujourd_hui
        - timedelta(days=aujourd_hui.weekday())
    )

    fin_semaine = (
        debut_semaine
        + timedelta(days=6)
    )

    debut_mois = aujourd_hui.replace(
        day=1
    )

    # =========================================================
    # COMPTEURS
    # =========================================================

    stats = {

        "activites": {

            "semaine": Activite.objects.filter(
                entreprise=entreprise,
                date__gte=debut_semaine,
                date__lte=fin_semaine
            ).count(),

            "mois": Activite.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante,
                date__month=aujourd_hui.month
            ).count(),

            "annee": Activite.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante
            ).count(),
        },

        "missions": {

            "semaine": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__gte=debut_semaine,
                date_depart__lte=fin_semaine
            ).count(),

            "mois": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__year=annee_courante,
                date_depart__month=aujourd_hui.month
            ).count(),

            "annee": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__year=annee_courante
            ).count(),
        },

        "rendez_vous": {

            "semaine": RendezVous.objects.filter(
                entreprise=entreprise,
                date__gte=debut_semaine,
                date__lte=fin_semaine
            ).count(),

            "mois": RendezVous.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante,
                date__month=aujourd_hui.month
            ).count(),

            "annee": RendezVous.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante
            ).count(),
        },
    }

    # =========================================================
    # DONNÉES DU GRAPHIQUE ANNUEL
    # =========================================================

    noms_mois = [
        "Jan",
        "Fév",
        "Mar",
        "Avr",
        "Mai",
        "Jun",
        "Jul",
        "Aoû",
        "Sep",
        "Oct",
        "Nov",
        "Déc",
    ]

    def repartition_mensuelle(queryset, champ_date):

        compteurs = [0] * 12

        donnees = (
            queryset
            .filter(
                **{
                    f"{champ_date}__year":
                    annee_courante
                }
            )
            .annotate(
                mois=TruncMonth(champ_date)
            )
            .values("mois")
            .annotate(
                total=Count("id")
            )
        )

        for ligne in donnees:

            compteurs[
                ligne["mois"].month - 1
            ] = ligne["total"]

        return compteurs

    graphique = {

        "labels": noms_mois,

        "activites": repartition_mensuelle(
            Activite.objects.filter(
                entreprise=entreprise
            ),
            "date"
        ),

        "missions": repartition_mensuelle(
            Mission.objects.filter(
                entreprise=entreprise
            ),
            "date_depart"
        ),

        "rendez_vous": repartition_mensuelle(
            RendezVous.objects.filter(
                entreprise=entreprise
            ),
            "date"
        ),
    }

    # =========================================================
    # RÉPARTITION DES ACTIVITÉS PAR STATUT
    # =========================================================

    repartition_statut_qs = (
        Activite.objects
        .filter(
            entreprise=entreprise
        )
        .values("statut")
        .annotate(
            total=Count("id")
        )
    )

    libelles_statut = dict(
        Activite.STATUT_CHOICES
    )

    repartition_statut = {

        "labels": [
            libelles_statut.get(
                ligne["statut"],
                ligne["statut"]
            )
            for ligne in repartition_statut_qs
        ],

        "valeurs": [
            ligne["total"]
            for ligne in repartition_statut_qs
        ],
    }

    # =========================================================
    # CONTEXTE DU DASHBOARD
    # =========================================================

    context = {

        # Anciennes données du dashboard
        "activites_a_venir": activites_a_venir,
        "activites_effectuees": activites_effectuees,
        "nombre_rendez_vous": nombre_rendez_vous,
        "nombre_missions": nombre_missions,
        "nombre_reunions": nombre_reunions,
        "nombre_comptes_rendus": nombre_comptes_rendus,

        # Statistiques
        "stats": stats,
        "annee_courante": annee_courante,
        "graphique_json": graphique,
        "repartition_statut_json": repartition_statut,
    }

    return render(
        request,
        "agenda/dashboard.html",
        context
    )


# =========================================================
# AGENDA
# =========================================================

@login_required
def agenda(request):

    aujourdhui = timezone.localdate()

    entreprise = request.user.entreprise

    annee = int(
        request.GET.get(
            "annee",
            aujourdhui.year
        )
    )

    mois = int(
        request.GET.get(
            "mois",
            aujourdhui.month
        )
    )

    cal = calendar.Calendar(
        firstweekday=0
    )

    semaines = cal.monthdatescalendar(
        annee,
        mois
    )

    # =========================================================
    # ACTIVITÉS
    # =========================================================

    activites = Activite.objects.filter(
        entreprise=entreprise,
        date__year=annee,
        date__month=mois
    )

    # =========================================================
    # RENDEZ-VOUS
    # =========================================================

    rendez_vous = RendezVous.objects.filter(
        entreprise=entreprise,
        date__year=annee,
        date__month=mois
    )

    evenements_par_jour = {}

    for a in activites:

        evenements_par_jour.setdefault(
            a.date,
            []
        ).append(
            {
                "type": "activite",
                "objet": a
            }
        )

    for r in rendez_vous:

        evenements_par_jour.setdefault(
            r.date,
            []
        ).append(
            {
                "type": "rendez_vous",
                "objet": r
            }
        )

    semaines_avec_evenements = []

    for semaine in semaines:

        jours = []

        for jour in semaine:

            jours.append(
                {
                    "date": jour,
                    "dans_le_mois": jour.month == mois,
                    "aujourdhui": jour == aujourdhui,
                    "evenements": evenements_par_jour.get(
                        jour,
                        []
                    ),
                }
            )

        semaines_avec_evenements.append(
            jours
        )

    mois_precedent = (
        mois - 1
        if mois > 1
        else 12
    )

    annee_mois_precedent = (
        annee
        if mois > 1
        else annee - 1
    )

    mois_suivant = (
        mois + 1
        if mois < 12
        else 1
    )

    annee_mois_suivant = (
        annee
        if mois < 12
        else annee + 1
    )

    context = {
        "semaines": semaines_avec_evenements,
        "nom_mois": calendar.month_name[
            mois
        ].capitalize(),
        "annee": annee,
        "mois_precedent": mois_precedent,
        "annee_mois_precedent": annee_mois_precedent,
        "mois_suivant": mois_suivant,
        "annee_mois_suivant": annee_mois_suivant,
    }

    return render(
        request,
        "agenda/agenda.html",
        context
    )


# =========================================================
# LISTES
# =========================================================

@login_required
def activites(request):

    entreprise = request.user.entreprise

    activites = Activite.objects.filter(
        entreprise=entreprise
    ).order_by(
        "-date",
        "-heure_debut"
    )

    return render(
        request,
        "agenda/activites.html",
        {
            "activites": activites
        }
    )


@login_required
def missions(request):

    entreprise = request.user.entreprise

    missions = Mission.objects.filter(
        entreprise=entreprise
    ).order_by(
        "-date_depart"
    )

    return render(
        request,
        "agenda/missions.html",
        {
            "missions": missions
        }
    )


@login_required
def rendez_vous(request):

    entreprise = request.user.entreprise

    rendez_vous = RendezVous.objects.filter(
        entreprise=entreprise
    ).order_by(
        "-date",
        "-heure"
    )

    return render(
        request,
        "agenda/rendez_vous.html",
        {
            "rendez_vous": rendez_vous
        }
    )


@login_required
def visiteurs(request):
    return render(
        request,
        "agenda/visiteurs.html"
    )


@login_required
def contacts(request):
    return render(
        request,
        "agenda/contacts.html"
    )


# =========================================================
# TÂCHES
# =========================================================

@login_required
def taches(request):

    entreprise = request.user.entreprise

    # =========================================================
    # DIRECTEUR
    # =========================================================

    if request.user.role == "directeur":

        taches = Tache.objects.filter(
            entreprise=entreprise
        )

    # =========================================================
    # ASSISTANT
    # =========================================================

    else:

        taches = Tache.objects.filter(
            entreprise=entreprise
        ).filter(
            Q(
                responsable=request.user
            )
            |
            Q(
                responsable__isnull=True,
                cree_par=request.user
            )
        )

    # =========================================================
    # OPTIMISATION + TRI
    # =========================================================

    taches = taches.select_related(
        "cree_par",
        "responsable"
    ).order_by(
        "statut",
        "date_echeance",
        "-date_creation"
    )

    return render(
        request,
        "agenda/taches.html",
        {
            "taches": taches,
        }
    )


@login_required
def nouvelle_tache(request):

    entreprise = request.user.entreprise

    # =========================================================
    # RESPONSABLES AUTORISÉS
    # =========================================================

    if request.user.role == "directeur":

        responsables = Utilisateur.objects.filter(
            entreprise=entreprise,
            role="assistant",
            statut_acces="actif"
        ).order_by(
            "first_name",
            "last_name",
            "username"
        )

    else:

        responsables = Utilisateur.objects.filter(
            pk=request.user.pk
        )

    # =========================================================
    # TRAITEMENT DU FORMULAIRE
    # =========================================================

    if request.method == "POST":

        form = TacheForm(
            request.POST,
            responsables=responsables
        )

        if form.is_valid():

            tache = form.save(
                commit=False
            )

            tache.cree_par = request.user
            tache.entreprise = entreprise

            if request.user.role != "directeur":

                tache.responsable = None

            tache.save()

            enregistrer_action(
                request.user,
                "Création de tâche",
                f"Tâche « {tache.titre} » créée"
            )

            return redirect(
                "taches"
            )

    else:

        form = TacheForm(
            responsables=responsables
        )

    return render(
        request,
        "agenda/nouvelle_tache.html",
        {
            "form": form,
        }
    )


# =========================================================
# COMPTES RENDUS
# =========================================================

@login_required
def comptes_rendus(request):

    comptes_rendus = (
        CompteRendu.objects
        .filter(
            entreprise=request.user.entreprise
        )
        .select_related(
            "reunion",
            "cree_par"
        )
        .order_by(
            "-date_redaction"
        )
    )

    return render(
        request,
        "agenda/comptes_rendus.html",
        {
            "comptes_rendus": comptes_rendus,
        }
    )


@login_required
def documents(request):
    return render(
        request,
        "agenda/documents.html"
    )


# =========================================================
# RAPPELS
# =========================================================

@login_required
def rappels(request):

    aujourd_hui = timezone.localdate()

    entreprise = request.user.entreprise

    activites = Activite.objects.filter(
        entreprise=entreprise,
        date__gte=aujourd_hui,
    ).exclude(
        rappel_minutes_avant=""
    ).order_by(
        "date",
        "heure_debut"
    )

    rendez_vous = RendezVous.objects.filter(
        entreprise=entreprise,
        date__gte=aujourd_hui,
    ).exclude(
        rappel_minutes_avant=""
    ).order_by(
        "date",
        "heure"
    )

    return render(
        request,
        "agenda/rappels.html",
        {
            "activites": activites,
            "rendez_vous": rendez_vous,
        }
    )


# =========================================================
# NOTIFICATIONS
# =========================================================

@login_required
def notifications(request):

    mes_notifications = Notification.objects.filter(
        destinataire=request.user
    )

    mes_notifications.filter(
        lue=False
    ).update(
        lue=True
    )

    return render(
        request,
        "agenda/notifications.html",
        {
            "notifications": mes_notifications
        }
    )

# =========================================================
# VÉRIFICATION AUTOMATIQUE DES RAPPELS
# =========================================================

def verifier_rappels_automatique(request):

    secret = request.headers.get("X-Rappels-Secret")

    if secret != settings.RAPPELS_SECRET:
        return JsonResponse(
            {
                "success": False,
                "message": "Accès non autorisé."
            },
            status=403
        )

    entreprises = Entreprise.objects.all()

    nombre = 0

    for entreprise in entreprises:
        verifier_rappels(entreprise)
        nombre += 1

    return JsonResponse(
        {
            "success": True,
            "message": f"{nombre} entreprise(s) vérifiée(s)."
        }
    )

# =========================================================
# RÉUNIONS
# =========================================================

@login_required
def reunions(request):

    entreprise = request.user.entreprise

    reunions = Reunion.objects.filter(
        entreprise=entreprise
    ).order_by(
        "-date",
        "-heure_debut"
    )

    return render(
        request,
        "agenda/reunions.html",
        {
            "reunions": reunions
        }
    )


# =========================================================
# STATISTIQUES
# =========================================================

@login_required
def statistiques(request):

    entreprise = request.user.entreprise

    aujourdhui = timezone.localdate()

    annee_courante = aujourdhui.year

    debut_semaine = (
        aujourdhui
        - timedelta(
            days=aujourdhui.weekday()
        )
    )

    fin_semaine = (
        debut_semaine
        + timedelta(days=6)
    )

    debut_mois = aujourdhui.replace(
        day=1
    )

    # =========================================================
    # COMPTEURS
    # =========================================================

    stats = {

        "activites": {

            "semaine": Activite.objects.filter(
                entreprise=entreprise,
                date__gte=debut_semaine,
                date__lte=fin_semaine
            ).count(),

            "mois": Activite.objects.filter(
                entreprise=entreprise,
                date__gte=debut_mois,
                date__year=annee_courante,
                date__month=aujourdhui.month
            ).count(),

            "annee": Activite.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante
            ).count(),
        },

        "missions": {

            "semaine": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__gte=debut_semaine,
                date_depart__lte=fin_semaine
            ).count(),

            "mois": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__year=annee_courante,
                date_depart__month=aujourdhui.month
            ).count(),

            "annee": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__year=annee_courante
            ).count(),
        },

        "rendez_vous": {

            "semaine": RendezVous.objects.filter(
                entreprise=entreprise,
                date__gte=debut_semaine,
                date__lte=fin_semaine
            ).count(),

            "mois": RendezVous.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante,
                date__month=aujourdhui.month
            ).count(),

            "annee": RendezVous.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante
            ).count(),
        },
    }

    # =========================================================
    # GRAPHIQUE ANNUEL
    # =========================================================

    noms_mois = [
        "Jan",
        "Fév",
        "Mar",
        "Avr",
        "Mai",
        "Jun",
        "Jul",
        "Aoû",
        "Sep",
        "Oct",
        "Nov",
        "Déc",
    ]

    def repartition_mensuelle(
        queryset,
        champ_date
    ):

        compteurs = [0] * 12

        donnees = (
            queryset
            .filter(
                **{
                    f"{champ_date}__year":
                    annee_courante
                }
            )
            .annotate(
                mois=TruncMonth(
                    champ_date
                )
            )
            .values(
                "mois"
            )
            .annotate(
                total=Count("id")
            )
        )

        for ligne in donnees:

            compteurs[
                ligne["mois"].month - 1
            ] = ligne["total"]

        return compteurs

    graphique = {

        "labels": noms_mois,

        "activites": repartition_mensuelle(
            Activite.objects.filter(
                entreprise=entreprise
            ),
            "date"
        ),

        "missions": repartition_mensuelle(
            Mission.objects.filter(
                entreprise=entreprise
            ),
            "date_depart"
        ),

        "rendez_vous": repartition_mensuelle(
            RendezVous.objects.filter(
                entreprise=entreprise
            ),
            "date"
        ),
    }

    # =========================================================
    # RÉPARTITION DES ACTIVITÉS PAR STATUT
    # =========================================================

    repartition_statut_qs = (
        Activite.objects
        .filter(
            entreprise=entreprise
        )
        .values(
            "statut"
        )
        .annotate(
            total=Count("id")
        )
    )

    libelles_statut = dict(
        Activite.STATUT_CHOICES
    )

    repartition_statut = {

        "labels": [
            libelles_statut.get(
                ligne["statut"],
                ligne["statut"]
            )
            for ligne in repartition_statut_qs
        ],

        "valeurs": [
            ligne["total"]
            for ligne in repartition_statut_qs
        ],
    }

    # =========================================================
    # CONTEXTE
    # =========================================================

    context = {

        "stats": stats,

        "annee_courante": annee_courante,

        "graphique_json": graphique,

        "repartition_statut_json": repartition_statut,
    }

    return render(
        request,
        "agenda/statistiques.html",
        context
    )


# =========================================================
# STATISTIQUES — DONNÉES JSON
# =========================================================

@login_required
def statistiques_data(request):

    entreprise = request.user.entreprise

    aujourdhui = timezone.localdate()

    annee_courante = aujourdhui.year

    debut_semaine = (
        aujourdhui
        - timedelta(
            days=aujourdhui.weekday()
        )
    )

    fin_semaine = (
        debut_semaine
        + timedelta(days=6)
    )

    # =========================================================
    # COMPTEURS
    # =========================================================

    stats = {

        "activites": {

            "semaine": Activite.objects.filter(
                entreprise=entreprise,
                date__gte=debut_semaine,
                date__lte=fin_semaine
            ).count(),

            "mois": Activite.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante,
                date__month=aujourdhui.month
            ).count(),

            "annee": Activite.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante
            ).count(),
        },

        "missions": {

            "semaine": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__gte=debut_semaine,
                date_depart__lte=fin_semaine
            ).count(),

            "mois": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__year=annee_courante,
                date_depart__month=aujourdhui.month
            ).count(),

            "annee": Mission.objects.filter(
                entreprise=entreprise,
                date_depart__year=annee_courante
            ).count(),
        },

        "rendez_vous": {

            "semaine": RendezVous.objects.filter(
                entreprise=entreprise,
                date__gte=debut_semaine,
                date__lte=fin_semaine
            ).count(),

            "mois": RendezVous.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante,
                date__month=aujourdhui.month
            ).count(),

            "annee": RendezVous.objects.filter(
                entreprise=entreprise,
                date__year=annee_courante
            ).count(),
        },
    }

    # =========================================================
    # GRAPHIQUE
    # =========================================================

    noms_mois = [
        "Jan",
        "Fév",
        "Mar",
        "Avr",
        "Mai",
        "Jun",
        "Jul",
        "Aoû",
        "Sep",
        "Oct",
        "Nov",
        "Déc",
    ]

    def repartition_mensuelle(
        queryset,
        champ_date
    ):

        compteurs = [0] * 12

        donnees = (
            queryset
            .filter(
                **{
                    f"{champ_date}__year":
                    annee_courante
                }
            )
            .annotate(
                mois=TruncMonth(
                    champ_date
                )
            )
            .values(
                "mois"
            )
            .annotate(
                total=Count("id")
            )
        )

        for ligne in donnees:

            compteurs[
                ligne["mois"].month - 1
            ] = ligne["total"]

        return compteurs

    graphique = {

        "labels": noms_mois,

        "activites": repartition_mensuelle(
            Activite.objects.filter(
                entreprise=entreprise
            ),
            "date"
        ),

        "missions": repartition_mensuelle(
            Mission.objects.filter(
                entreprise=entreprise
            ),
            "date_depart"
        ),

        "rendez_vous": repartition_mensuelle(
            RendezVous.objects.filter(
                entreprise=entreprise
            ),
            "date"
        ),
    }

    return JsonResponse(
        {
            "stats": stats,
            "graphique": graphique
        }
    )


# =========================================================
# HISTORIQUE
# =========================================================

@login_required
def historique(request):

    entreprise = request.user.entreprise

    actions = (
        HistoriqueAction.objects
        .filter(
            entreprise=entreprise
        )
        .order_by(
            "-date"
        )
    )

    recherche = request.GET.get(
        "recherche",
        ""
    ).strip()

    if recherche:

        actions = (
            actions.filter(
                utilisateur__username__icontains=recherche
            )
            |
            actions.filter(
                action__icontains=recherche
            )
            |
            actions.filter(
                description__icontains=recherche
            )
        )

    type_action = request.GET.get(
        "type_action",
        ""
    ).strip()

    if type_action:

        actions = actions.filter(
            action=type_action
        )

    actions = actions[:200]

    types_actions = (
        HistoriqueAction.objects
        .filter(
            entreprise=entreprise
        )
        .values_list(
            "action",
            flat=True
        )
        .distinct()
        .order_by(
            "action"
        )
    )

    context = {

        "actions": actions,

        "recherche": recherche,

        "type_action": type_action,

        "types_actions": types_actions,
    }

    return render(
        request,
        "agenda/historique.html",
        context
    )


# =========================================================
# ASSISTANTS
# =========================================================

@login_required
def assistants(request):
    return render(
        request,
        "agenda/assistants.html"
    )


# =========================================================
# PARAMÈTRES
# =========================================================

@login_required
def parametres(request):
    return render(
        request,
        "agenda/parametres.html"
    )


# =========================================================
# ACTIVITÉS — CRUD
# =========================================================

@login_required
def nouvelle_activite(request):

    if request.method == "POST":

        form = ActiviteForm(
            request.POST
        )

        if form.is_valid():

            activite = form.save(
                commit=False
            )

            activite.cree_par = request.user
            activite.entreprise = request.user.entreprise

            activite.save()

            enregistrer_action(
                request.user,
                "Création d'activité",
                f"Activité « {activite.objet} » créée"
            )

            if activite.statut == "en_attente":

                directeurs = Utilisateur.objects.filter(
                    entreprise=request.user.entreprise,
                    role="directeur"
                )

                for directeur in directeurs:

                    creer_notification(
                        directeur,
                        f"Nouvelle activité à valider : « {activite.objet} »",
                        lien="/activites/",
                    )

            return redirect(
                "activites"
            )

    else:

        form = ActiviteForm()

    return render(
        request,
        "agenda/nouvelle_activite.html",
        {
            "form": form
        }
    )


@login_required
def modifier_activite(request, pk):

    activite = get_object_or_404(
        Activite,
        pk=pk,
        entreprise=request.user.entreprise
    )

    ancien_statut = activite.statut

    if request.method == "POST":

        form = ActiviteForm(
            request.POST,
            instance=activite
        )

        if form.is_valid():

            activite = form.save()

            enregistrer_action(
                request.user,
                "Modification d'activité",
                f"Activité « {activite.objet} » modifiée"
            )

            if (
                ancien_statut == "en_attente"
                and activite.statut in [
                    "confirmee",
                    "annulee"
                ]
            ):

                verbe = (
                    "confirmée"
                    if activite.statut == "confirmee"
                    else "refusée"
                )

                creer_notification(
                    activite.cree_par,
                    f"Votre activité « {activite.objet} » a été {verbe}",
                    lien="/activites/",
                )

            return redirect(
                "activites"
            )

    else:

        form = ActiviteForm(
            instance=activite
        )

    return render(
        request,
        "agenda/nouvelle_activite.html",
        {
            "form": form,
            "modification": True
        }
    )


@login_required
def supprimer_activite(request, pk):

    activite = get_object_or_404(
        Activite,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        objet = activite.objet

        activite.delete()

        enregistrer_action(
            request.user,
            "Suppression d'activité",
            f"Activité « {objet} » supprimée"
        )

        return redirect(
            "activites"
        )

    return render(
        request,
        "agenda/supprimer_activite.html",
        {
            "activite": activite
        }
    )


# =========================================================
# MISSIONS — CRUD
# =========================================================

@login_required
def nouvelle_mission(request):

    if request.method == "POST":

        form = MissionForm(
            request.POST
        )

        if form.is_valid():

            mission = form.save(
                commit=False
            )

            mission.cree_par = request.user
            mission.entreprise = request.user.entreprise

            mission.save()

            enregistrer_action(
                request.user,
                "Création de mission",
                f"Mission « {mission.motif} » créée"
            )

            if request.user.role == "assistant":

                directeurs = Utilisateur.objects.filter(
                    entreprise=request.user.entreprise,
                    role="directeur"
                )

                for directeur in directeurs:

                    creer_notification(
                        directeur,
                        f"Nouvelle mission ajoutée : « {mission.motif} »",
                        lien="/missions/",
                    )

            return redirect(
                "missions"
            )

    else:

        form = MissionForm()

    return render(
        request,
        "agenda/nouvelle_mission.html",
        {
            "form": form
        }
    )


@login_required
def modifier_mission(request, pk):

    mission = get_object_or_404(
        Mission,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        form = MissionForm(
            request.POST,
            instance=mission
        )

        if form.is_valid():

            form.save()

            enregistrer_action(
                request.user,
                "Modification de mission",
                f"Mission « {mission.motif} » modifiée"
            )

            return redirect(
                "missions"
            )

    else:

        form = MissionForm(
            instance=mission
        )

    return render(
        request,
        "agenda/nouvelle_mission.html",
        {
            "form": form,
            "modification": True
        }
    )


@login_required
def supprimer_mission(request, pk):

    mission = get_object_or_404(
        Mission,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        motif = mission.motif

        mission.delete()

        enregistrer_action(
            request.user,
            "Suppression de mission",
            f"Mission « {motif} » supprimée"
        )

        return redirect(
            "missions"
        )

    return render(
        request,
        "agenda/supprimer_mission.html",
        {
            "mission": mission
        }
    )


# =========================================================
# RENDEZ-VOUS — CRUD
# =========================================================

@login_required
def nouveau_rendez_vous(request):

    if request.method == "POST":

        form = RendezVousForm(
            request.POST
        )

        if form.is_valid():

            rdv = form.save(
                commit=False
            )

            rdv.cree_par = request.user
            rdv.entreprise = request.user.entreprise

            rdv.save()

            enregistrer_action(
                request.user,
                "Création de rendez-vous",
                f"Rendez-vous « {rdv.objet} » créé"
            )

            if request.user.role == "assistant":

                directeurs = Utilisateur.objects.filter(
                    entreprise=request.user.entreprise,
                    role="directeur"
                )

                for directeur in directeurs:

                    creer_notification(
                        directeur,
                        f"Nouveau rendez-vous ajouté : « {rdv.objet} »",
                        lien="/rendez-vous/",
                    )

            return redirect(
                "rendez_vous"
            )

    else:

        form = RendezVousForm()

    return render(
        request,
        "agenda/nouveau_rendez_vous.html",
        {
            "form": form
        }
    )


@login_required
def modifier_rendez_vous(request, pk):

    rdv = get_object_or_404(
        RendezVous,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        form = RendezVousForm(
            request.POST,
            instance=rdv
        )

        if form.is_valid():

            form.save()

            enregistrer_action(
                request.user,
                "Modification de rendez-vous",
                f"Rendez-vous « {rdv.objet} » modifié"
            )

            return redirect(
                "rendez_vous"
            )

    else:

        form = RendezVousForm(
            instance=rdv
        )

    return render(
        request,
        "agenda/nouveau_rendez_vous.html",
        {
            "form": form,
            "modification": True
        }
    )


@login_required
def supprimer_rendez_vous(request, pk):

    rdv = get_object_or_404(
        RendezVous,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        objet = rdv.objet

        rdv.delete()

        enregistrer_action(
            request.user,
            "Suppression de rendez-vous",
            f"Rendez-vous « {objet} » supprimé"
        )

        return redirect(
            "rendez_vous"
        )

    return render(
        request,
        "agenda/supprimer_rendez_vous.html",
        {
            "rendez_vous": rdv
        }
    )


# =========================================================
# RÉUNIONS — CRUD
# =========================================================

@login_required
def nouvelle_reunion(request):

    if request.method == "POST":

        form = ReunionForm(
            request.POST
        )

        if form.is_valid():

            reunion = form.save(
                commit=False
            )

            reunion.cree_par = request.user
            reunion.entreprise = request.user.entreprise

            reunion.save()

            enregistrer_action(
                request.user,
                "Création de réunion",
                f"Réunion « {reunion.titre} » créée"
            )

            return redirect(
                "reunions"
            )

    else:

        form = ReunionForm()

    return render(
        request,
        "agenda/nouvelle_reunion.html",
        {
            "form": form
        }
    )


@login_required
def modifier_reunion(request, pk):

    reunion = get_object_or_404(
        Reunion,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        form = ReunionForm(
            request.POST,
            instance=reunion
        )

        if form.is_valid():

            reunion = form.save()

            enregistrer_action(
                request.user,
                "Modification de réunion",
                f"Réunion « {reunion.titre} » modifiée"
            )

            return redirect(
                "reunions"
            )

    else:

        form = ReunionForm(
            instance=reunion
        )

    return render(
        request,
        "agenda/nouvelle_reunion.html",
        {
            "form": form,
            "modification": True
        }
    )


@login_required
def supprimer_reunion(request, pk):

    reunion = get_object_or_404(
        Reunion,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        titre = reunion.titre

        reunion.delete()

        enregistrer_action(
            request.user,
            "Suppression de réunion",
            f"Réunion « {titre} » supprimée"
        )

        return redirect(
            "reunions"
        )

    return render(
        request,
        "agenda/supprimer_reunion.html",
        {
            "reunion": reunion
        }
    )


# =========================================================
# COMPTES RENDUS — CRUD
# =========================================================

@login_required
def nouveau_compte_rendu(request, pk):

    reunion = get_object_or_404(
        Reunion,
        pk=pk,
        entreprise=request.user.entreprise
    )

    # =========================================================
    # UNE RÉUNION = UN SEUL COMPTE RENDU
    # =========================================================

    compte_rendu_existant = (
        CompteRendu.objects
        .filter(
            reunion=reunion
        )
        .first()
    )

    if compte_rendu_existant:

        return redirect(
            "modifier_compte_rendu",
            pk=compte_rendu_existant.pk
        )

    if request.method == "POST":

        form = CompteRenduForm(
            request.POST
        )

        if form.is_valid():

            compte_rendu = form.save(
                commit=False
            )

            compte_rendu.reunion = reunion

            compte_rendu.cree_par = request.user

            compte_rendu.entreprise = request.user.entreprise

            compte_rendu.save()

            enregistrer_action(
                request.user,
                "Création de compte rendu",
                f"Compte rendu de la réunion « {reunion.titre} » créé"
            )

            return redirect(
                "reunions"
            )

    else:

        form = CompteRenduForm(
            initial={
                "participants": reunion.participants,
            }
        )

    return render(
        request,
        "agenda/nouveau_compte_rendu.html",
        {
            "form": form,
            "reunion": reunion,
        }
    )


# =========================================================
# MODIFIER UN COMPTE RENDU
# =========================================================

@login_required
def modifier_compte_rendu(request, pk):

    compte_rendu = get_object_or_404(
        CompteRendu,
        pk=pk,
        entreprise=request.user.entreprise
    )

    if request.method == "POST":

        form = CompteRenduForm(
            request.POST,
            instance=compte_rendu
        )

        if form.is_valid():

            compte_rendu = form.save()

            enregistrer_action(
                request.user,
                "Modification de compte rendu",
                f"Compte rendu de la réunion « {compte_rendu.reunion.titre} » modifié"
            )

            return redirect(
                "reunions"
            )

    else:

        form = CompteRenduForm(
            instance=compte_rendu
        )

    return render(
        request,
        "agenda/nouveau_compte_rendu.html",
        {
            "form": form,
            "reunion": compte_rendu.reunion,
            "modification": True,
        }
    )


@login_required
def voir_compte_rendu(request, pk):

    compte_rendu = get_object_or_404(
        CompteRendu,
        pk=pk,
        entreprise=request.user.entreprise
    )

    return render(
        request,
        "agenda/voir_compte_rendu.html",
        {
            "compte_rendu": compte_rendu,
            "reunion": compte_rendu.reunion,
        }
    )


# =========================================================
# ARCHIVES
# =========================================================

@login_required
def archives(request):

    entreprise = request.user.entreprise

    activites_archivees = (
        Activite.objects
        .filter(
            entreprise=entreprise,
            statut="effectuee"
        )
        .order_by(
            "-date"
        )
    )

    missions_archivees = (
        Mission.objects
        .filter(
            entreprise=entreprise,
            statut="terminee"
        )
        .order_by(
            "-date_depart"
        )
    )

    rendez_vous_archives = (
        RendezVous.objects
        .filter(
            entreprise=entreprise,
            statut__in=[
                "termine",
                "annule"
            ]
        )
        .order_by(
            "-date"
        )
    )

    context = {

        "activites_archivees":
            activites_archivees,

        "missions_archivees":
            missions_archivees,

        "rendez_vous_archives":
            rendez_vous_archives,
    }

    return render(
        request,
        "agenda/archives.html",
        context
    )


# =========================================================
# ACTIVITÉ — PDF
# =========================================================

@login_required
def activite_pdf(request, pk):

    activite = get_object_or_404(
        Activite,
        pk=pk,
        entreprise=request.user.entreprise
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="activite_{activite.pk}.pdf"'
    )

    p = canvas.Canvas(
        response,
        pagesize=A4
    )

    largeur, hauteur = A4

    y = hauteur - 60

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        50,
        y,
        "DIRAGENDA — Fiche d'activité"
    )

    y -= 40

    p.setFont(
        "Helvetica-Bold",
        12
    )

    p.drawString(
        50,
        y,
        "Objet :"
    )

    p.setFont(
        "Helvetica",
        12
    )

    p.drawString(
        150,
        y,
        activite.objet
    )

    y -= 25

    champs = [

        (
            "Date",
            activite.date.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Date de fin",
            activite.date_fin.strftime(
                "%d/%m/%Y"
            )
            if activite.date_fin
            else "—"
        ),

        (
            "Heure début",
            activite.heure_debut.strftime(
                "%H:%M"
            )
            if activite.heure_debut
            else "—"
        ),

        (
            "Heure fin",
            activite.heure_fin.strftime(
                "%H:%M"
            )
            if activite.heure_fin
            else "—"
        ),

        (
            "Lieu",
            activite.lieu or "—"
        ),

        (
            "Contact",
            activite.contact or "—"
        ),

        (
            "Statut",
            activite.get_statut_display()
        ),

        (
            "Créé par",
            str(activite.cree_par)
        ),
    ]

    p.setFont(
        "Helvetica-Bold",
        12
    )

    for label, valeur in champs:

        p.drawString(
            50,
            y,
            f"{label} :"
        )

        p.setFont(
            "Helvetica",
            12
        )

        p.drawString(
            150,
            y,
            str(valeur)
        )

        p.setFont(
            "Helvetica-Bold",
            12
        )

        y -= 22

    y -= 10

    p.drawString(
        50,
        y,
        "Observations :"
    )

    p.setFont(
        "Helvetica",
        11
    )

    y -= 20

    for ligne in (
        activite.observations or "—"
    ).split("\n"):

        p.drawString(
            50,
            y,
            ligne
        )

        y -= 16

    p.showPage()

    p.save()

    return response


# =========================================================
# ACTIVITÉ — WORD
# =========================================================

@login_required
def activite_word(request, pk):

    activite = get_object_or_404(
        Activite,
        pk=pk,
        entreprise=request.user.entreprise
    )

    document = Document()

    document.add_heading(
        "DIRAGENDA — Fiche d'activité",
        level=1
    )

    table = document.add_table(
        rows=0,
        cols=2
    )

    table.style = "Light Grid Accent 1"

    lignes = [

        (
            "Objet",
            activite.objet
        ),

        (
            "Date",
            activite.date.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Date de fin",
            activite.date_fin.strftime(
                "%d/%m/%Y"
            )
            if activite.date_fin
            else "—"
        ),

        (
            "Heure début",
            activite.heure_debut.strftime(
                "%H:%M"
            )
            if activite.heure_debut
            else "—"
        ),

        (
            "Heure fin",
            activite.heure_fin.strftime(
                "%H:%M"
            )
            if activite.heure_fin
            else "—"
        ),

        (
            "Lieu",
            activite.lieu or "—"
        ),

        (
            "Contact",
            activite.contact or "—"
        ),

        (
            "Statut",
            activite.get_statut_display()
        ),

        (
            "Créé par",
            str(activite.cree_par)
        ),
    ]

    for label, valeur in lignes:

        row = table.add_row().cells

        row[0].text = label

        row[1].text = str(
            valeur
        )

    document.add_heading(
        "Observations",
        level=2
    )

    document.add_paragraph(
        activite.observations or "—"
    )

    response = HttpResponse(
        content_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="activite_{activite.pk}.docx"'
    )

    document.save(
        response
    )

    return response


# =========================================================
# MISSION — PDF
# =========================================================

@login_required
def mission_pdf(request, pk):

    mission = get_object_or_404(
        Mission,
        pk=pk,
        entreprise=request.user.entreprise
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="mission_{mission.pk}.pdf"'
    )

    p = canvas.Canvas(
        response,
        pagesize=A4
    )

    largeur, hauteur = A4

    y = hauteur - 60

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        50,
        y,
        "DIRAGENDA — Fiche de mission"
    )

    y -= 40

    champs = [

        (
            "Motif",
            mission.motif
        ),

        (
            "Lieu",
            mission.lieu
        ),

        (
            "Date de départ",
            mission.date_depart.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Date de retour",
            mission.date_retour.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Statut",
            mission.get_statut_display()
        ),

        (
            "Créé par",
            str(mission.cree_par)
        ),
    ]

    p.setFont(
        "Helvetica-Bold",
        12
    )

    for label, valeur in champs:

        p.drawString(
            50,
            y,
            f"{label} :"
        )

        p.setFont(
            "Helvetica",
            12
        )

        p.drawString(
            180,
            y,
            str(valeur)
        )

        p.setFont(
            "Helvetica-Bold",
            12
        )

        y -= 25

    p.showPage()

    p.save()

    return response


# =========================================================
# MISSION — WORD
# =========================================================

@login_required
def mission_word(request, pk):

    mission = get_object_or_404(
        Mission,
        pk=pk,
        entreprise=request.user.entreprise
    )

    document = Document()

    document.add_heading(
        "DIRAGENDA — Fiche de mission",
        level=1
    )

    table = document.add_table(
        rows=0,
        cols=2
    )

    table.style = "Light Grid Accent 1"

    lignes = [

        (
            "Motif",
            mission.motif
        ),

        (
            "Lieu",
            mission.lieu
        ),

        (
            "Date de départ",
            mission.date_depart.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Date de retour",
            mission.date_retour.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Statut",
            mission.get_statut_display()
        ),

        (
            "Créé par",
            str(mission.cree_par)
        ),
    ]

    for label, valeur in lignes:

        row = table.add_row().cells

        row[0].text = label

        row[1].text = str(
            valeur
        )

    response = HttpResponse(
        content_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="mission_{mission.pk}.docx"'
    )

    document.save(
        response
    )

    return response


# =========================================================
# RENDEZ-VOUS — PDF
# =========================================================

@login_required
def rendez_vous_pdf(request, pk):

    rdv = get_object_or_404(
        RendezVous,
        pk=pk,
        entreprise=request.user.entreprise
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="rendez_vous_{rdv.pk}.pdf"'
    )

    p = canvas.Canvas(
        response,
        pagesize=A4
    )

    largeur, hauteur = A4

    y = hauteur - 60

    p.setFont(
        "Helvetica-Bold",
        16
    )

    p.drawString(
        50,
        y,
        "DIRAGENDA — Fiche de rendez-vous"
    )

    y -= 40

    champs = [

        (
            "Objet",
            rdv.objet
        ),

        (
            "Date",
            rdv.date.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Heure",
            rdv.heure.strftime(
                "%H:%M"
            )
            if rdv.heure
            else "—"
        ),

        (
            "Lieu",
            rdv.lieu or "—"
        ),

        (
            "Personne",
            rdv.personne or "—"
        ),

        (
            "Téléphone",
            rdv.telephone or "—"
        ),

        (
            "Statut",
            rdv.get_statut_display()
        ),

        (
            "Créé par",
            str(rdv.cree_par)
        ),
    ]

    p.setFont(
        "Helvetica-Bold",
        12
    )

    for label, valeur in champs:

        p.drawString(
            50,
            y,
            f"{label} :"
        )

        p.setFont(
            "Helvetica",
            12
        )

        p.drawString(
            180,
            y,
            str(valeur)
        )

        p.setFont(
            "Helvetica-Bold",
            12
        )

        y -= 22

    y -= 10

    p.drawString(
        50,
        y,
        "Observations :"
    )

    p.setFont(
        "Helvetica",
        11
    )

    y -= 20

    for ligne in (
        rdv.observations or "—"
    ).split("\n"):

        p.drawString(
            50,
            y,
            ligne
        )

        y -= 16

    p.showPage()

    p.save()

    return response


# =========================================================
# RENDEZ-VOUS — WORD
# =========================================================

@login_required
def rendez_vous_word(request, pk):

    rdv = get_object_or_404(
        RendezVous,
        pk=pk,
        entreprise=request.user.entreprise
    )

    document = Document()

    document.add_heading(
        "DIRAGENDA — Fiche de rendez-vous",
        level=1
    )

    table = document.add_table(
        rows=0,
        cols=2
    )

    table.style = "Light Grid Accent 1"

    lignes = [

        (
            "Objet",
            rdv.objet
        ),

        (
            "Date",
            rdv.date.strftime(
                "%d/%m/%Y"
            )
        ),

        (
            "Heure",
            rdv.heure.strftime(
                "%H:%M"
            )
            if rdv.heure
            else "—"
        ),

        (
            "Lieu",
            rdv.lieu or "—"
        ),

        (
            "Personne",
            rdv.personne or "—"
        ),

        (
            "Téléphone",
            rdv.telephone or "—"
        ),

        (
            "Statut",
            rdv.get_statut_display()
        ),

        (
            "Créé par",
            str(rdv.cree_par)
        ),
    ]

    for label, valeur in lignes:

        row = table.add_row().cells

        row[0].text = label

        row[1].text = str(
            valeur
        )

    document.add_heading(
        "Observations",
        level=2
    )

    document.add_paragraph(
        rdv.observations or "—"
    )

    response = HttpResponse(
        content_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        f'attachment; '
        f'filename="rendez_vous_{rdv.pk}.docx"'
    )

    document.save(
        response
    )

    return response


# =========================================================
# WEB PUSH — ABONNEMENT
# =========================================================

@login_required
def push_public_key(request):

    try:
        with open(
            settings.VAPID_PUBLIC_KEY_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            public_key = f.read()

        return JsonResponse({
            "public_key": public_key
        })

    except FileNotFoundError:

        return JsonResponse(
            {
                "error": "Clé publique VAPID introuvable."
            },
            status=500
        )


@login_required
def push_subscribe(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "error": "Méthode non autorisée."
            },
            status=405
        )

    try:
        import json
        import hashlib

        data = json.loads(request.body)

        endpoint = data.get("endpoint")
        keys = data.get("keys", {})

        p256dh = keys.get("p256dh")
        auth = keys.get("auth")

        if not endpoint or not p256dh or not auth:
            return JsonResponse(
                {
                    "error": "Données d'abonnement incomplètes."
                },
                status=400
            )

        endpoint_hash = hashlib.sha256(
            endpoint.encode("utf-8")
        ).hexdigest()

        abonnement, created = PushSubscription.objects.update_or_create(
            endpoint_hash=endpoint_hash,
            defaults={
                "utilisateur": request.user,
                "endpoint": endpoint,
                "p256dh": p256dh,
                "auth": auth,
            }
        )

        return JsonResponse({
            "success": True,
            "created": created,
            "message": "Abonnement Push enregistré."
        })

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "JSON invalide."
            },
            status=400
        )

    except Exception as e:

        return JsonResponse(
            {
                "error": str(e)
            },
            status=500
        )





# =========================================================
# SERVICE WORKER
# =========================================================

def service_worker(request):

    with open(
        settings.BASE_DIR
        / "static"
        / "service-worker.js",
        "r"
    ) as f:

        contenu = f.read()

    return HttpResponse(
        contenu,
        content_type="application/javascript"
    )
    
    
# =========================================================
# WEB PUSH — NOTIFICATIONS
# =========================================================

import base64
from cryptography.hazmat.primitives import serialization


@login_required
def push_public_key(request):
    """
    Retourne la clé publique VAPID dans le format
    attendu par PushManager.subscribe().
    """

    with open(settings.VAPID_PUBLIC_KEY_PATH, "rb") as fichier:
        cle_pem = fichier.read()

    cle_publique = serialization.load_pem_public_key(cle_pem)

    cle_brute = cle_publique.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )

    cle_base64 = base64.urlsafe_b64encode(
        cle_brute
    ).rstrip(b"=").decode("ascii")

    return JsonResponse({
        "publicKey": cle_base64
    })


@login_required
def push_subscribe(request):
    """
    Enregistre l'abonnement Push du navigateur.
    """

    if request.method != "POST":
        return JsonResponse(
            {"success": False, "message": "Méthode non autorisée."},
            status=405,
        )

    try:
        donnees = json.loads(request.body)

        endpoint = donnees.get("endpoint")
        keys = donnees.get("keys", {})

        p256dh = keys.get("p256dh")
        auth = keys.get("auth")

        if not endpoint or not p256dh or not auth:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Données d'abonnement incomplètes.",
                },
                status=400,
            )

        import hashlib

        endpoint_hash = hashlib.sha256(
            endpoint.encode("utf-8")
        ).hexdigest()

        abonnement, cree = PushSubscription.objects.update_or_create(
            endpoint_hash=endpoint_hash,
            defaults={
                "utilisateur": request.user,
                "endpoint": endpoint,
                "p256dh": p256dh,
                "auth": auth,
            },
        )

        return JsonResponse({
            "success": True,
            "created": cree,
            "message": "Notifications Push activées.",
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "success": False,
                "message": "JSON invalide.",
            },
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "message": str(e),
            },
            status=500,
        )    