from .models import HistoriqueAction
from .models import Notification

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