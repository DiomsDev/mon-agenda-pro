from .models import Notification
from .utils import verifier_rappels


def notifications_non_lues(request):
    if request.user.is_authenticated:
        if request.user.entreprise:
            verifier_rappels(request.user.entreprise)
        count = Notification.objects.filter(destinataire=request.user, lue=False).count()
        return {"notifications_non_lues": count}
    return {"notifications_non_lues": 0}