from .models import HistoriqueAction


def enregistrer_action(utilisateur, action, description=""):
    HistoriqueAction.objects.create(
        utilisateur=utilisateur,
        entreprise=utilisateur.entreprise,
        action=action,
        description=description,
    )