from .models import HistoriqueAction
from .models import Notification
from .models import PushSubscription

from django.conf import settings
from django.utils import timezone

from datetime import timedelta, datetime

import json
import logging

from pywebpush import webpush, WebPushException


logger = logging.getLogger(__name__)



# =========================================================
# ENVOYER UNE NOTIFICATION PUSH
# =========================================================

def envoyer_push(destinataire, message, lien=""):

    abonnements = PushSubscription.objects.filter(
        utilisateur=destinataire
    )

    if not abonnements.exists():
        return

    donnees = json.dumps({
        "title": "DIRAGENDA",
        "body": message,
        "url": lien or "/",
    })

    for abonnement in abonnements:

        subscription_info = {
            "endpoint": abonnement.endpoint,
            "keys": {
                "p256dh": abonnement.p256dh,
                "auth": abonnement.auth,
            },
        }

        try:

            webpush(
                subscription_info=subscription_info,
                data=donnees,
                vapid_private_key=str(
                    settings.VAPID_PRIVATE_KEY_PATH
                ),
                vapid_claims={
                    "sub": settings.VAPID_EMAIL
                },
            )

        except WebPushException as erreur:

            response = getattr(
                erreur,
                "response",
                None
            )

            status_code = getattr(
                response,
                "status_code",
                None
            )

            # L'abonnement n'existe plus
            if status_code in (404, 410):

                abonnement.delete()

            else:

                logger.error(
                    "Erreur Web Push pour %s : %s",
                    destinataire,
                    erreur
                )

        except Exception as erreur:

            logger.error(
                "Erreur inattendue Web Push pour %s : %s",
                destinataire,
                erreur
            )
            
            
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

    notification = Notification.objects.create(
        destinataire=destinataire,
        entreprise=entreprise or destinataire.entreprise,
        message=message,
        lien=lien,
    )

    # Envoyer également la notification en Push
    envoyer_push(
        destinataire=destinataire,
        message=message,
        lien=lien,
    )

    return notification


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