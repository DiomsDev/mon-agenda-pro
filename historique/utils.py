from .models import HistoriqueAction


def enregistrer_action(utilisateur, action, description=""):
    HistoriqueAction.objects.create(
        utilisateur=utilisateur,
        action=action,
        description=description,
    )