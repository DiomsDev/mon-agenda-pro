from .models import HistoriqueAction
from .models import Notification

from django.utils import timezone
from datetime import timedelta, datetime


# =========================================================
# ENREGISTRER UNE ACTION
# =========================================================

def enregistrer_action(utilisateur, action, description=""):
    HistoriqueAction.objects.create(
        utilisateur=utilisateur,
        entreprise=utilisateur.entreprise,
        action=action,
        description=description,
    )


# =========================================================
# CRÉER UNE NOTIFICATION
# =========================================================

def creer_notification(
    destinataire,
    message,
    lien="",
    entreprise=None
):
    Notification.objects.create(
        destinataire=destinataire,
        entreprise=entreprise or destinataire.entreprise,
        message=message,
        lien=lien,
    )


# =========================================================
# VÉRIFIER LES RAPPELS
# =========================================================

def verifier_rappels(entreprise):

    from agenda.models import (
        Activite,
        RendezVous,
        Reunion,
    )

    maintenant = timezone.now()

    # =====================================================
    # ACTIVITÉS
    # =====================================================

    activites = Activite.objects.filter(
        entreprise=entreprise,
        rappel_envoye=False,
    ).exclude(
        rappel_minutes_avant=""
    )

    for activite in activites:

        if not activite.heure_debut:
            continue

        date_heure_evenement = timezone.make_aware(
            datetime.combine(
                activite.date,
                activite.heure_debut
            )
        )

        moment_rappel = (
            date_heure_evenement
            - timedelta(
                minutes=int(activite.rappel_minutes_avant)
            )
        )

        if maintenant >= moment_rappel:

            creer_notification(
                activite.cree_par,
                (
                    f"⏰ Rappel : Activité "
                    f"« {activite.objet} » "
                    f"à {activite.heure_debut.strftime('%H:%M')}"
                ),
                lien="/activites/",
            )

            activite.rappel_envoye = True

            activite.save(
                update_fields=["rappel_envoye"]
            )


    # =====================================================
    # RENDEZ-VOUS
    # =====================================================

    rendez_vous = RendezVous.objects.filter(
        entreprise=entreprise,
        rappel_envoye=False,
    ).exclude(
        rappel_minutes_avant=""
    )

    for rendez_vous_item in rendez_vous:

        if not rendez_vous_item.heure:
            continue

        date_heure_evenement = timezone.make_aware(
            datetime.combine(
                rendez_vous_item.date,
                rendez_vous_item.heure
            )
        )

        moment_rappel = (
            date_heure_evenement
            - timedelta(
                minutes=int(
                    rendez_vous_item.rappel_minutes_avant
                )
            )
        )

        if maintenant >= moment_rappel:

            creer_notification(
                rendez_vous_item.cree_par,
                (
                    f"⏰ Rappel : Rendez-vous "
                    f"« {rendez_vous_item.objet} » "
                    f"à {rendez_vous_item.heure.strftime('%H:%M')}"
                ),
                lien="/rendez-vous/",
            )

            rendez_vous_item.rappel_envoye = True

            rendez_vous_item.save(
                update_fields=["rappel_envoye"]
            )


    # =====================================================
    # RÉUNIONS
    # =====================================================

    reunions = Reunion.objects.filter(
        entreprise=entreprise,
        rappel_envoye=False,
    ).exclude(
        rappel_minutes_avant=""
    )

    for reunion in reunions:

        if not reunion.heure_debut:
            continue

        date_heure_evenement = timezone.make_aware(
            datetime.combine(
                reunion.date,
                reunion.heure_debut
            )
        )

        moment_rappel = (
            date_heure_evenement
            - timedelta(
                minutes=int(
                    reunion.rappel_minutes_avant
                )
            )
        )

        if maintenant >= moment_rappel:

            creer_notification(
                reunion.cree_par,
                (
                    f"⏰ Rappel : Réunion "
                    f"« {reunion.titre} » "
                    f"à {reunion.heure_debut.strftime('%H:%M')}"
                ),
                lien="/reunions/",
            )

            reunion.rappel_envoye = True

            reunion.save(
                update_fields=["rappel_envoye"]
            )