from .models import HistoriqueAction
from .models import Notification

from django.utils import timezone
from datetime import timedelta, datetime

def enregistrer_action(utilisateur, action, description=""):
    HistoriqueAction.objects.create(
        utilisateur=utilisateur,
        entreprise=utilisateur.entreprise,
        action=action,
        description=description,
    )
    




def creer_notification(destinataire, message, lien="", entreprise=None):
    Notification.objects.create(
        destinataire=destinataire,
        entreprise=entreprise or destinataire.entreprise,
        message=message,
        lien=lien,
    )    
    





def verifier_rappels(entreprise):
    from agenda.models import Activite, RendezVous

    maintenant = timezone.now()

    for modele, nom_champ_heure, type_libelle, lien in [
        (Activite, "heure_debut", "Activité", "/activites/"),
        (RendezVous, "heure", "Rendez-vous", "/rendez-vous/"),
    ]:
        items = modele.objects.filter(
            entreprise=entreprise,
            rappel_envoye=False,
        ).exclude(rappel_minutes_avant="")

        for item in items:
            heure = getattr(item, nom_champ_heure)
            if not heure:
                continue

            date_heure_evenement = timezone.make_aware(
                datetime.combine(item.date, heure)
            )
            moment_rappel = date_heure_evenement - timedelta(minutes=int(item.rappel_minutes_avant))

            if maintenant >= moment_rappel:
                creer_notification(
                    item.cree_par,
                    f"⏰ Rappel : {type_libelle} « {item.objet} » à {heure.strftime('%H:%M')}",
                    lien=lien,
                )
                item.rappel_envoye = True
                item.save(update_fields=["rappel_envoye"])    