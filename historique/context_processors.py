from .models import Notification


def notifications_non_lues(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(destinataire=request.user, lue=False).count()
        return {"notifications_non_lues": count}
    return {"notifications_non_lues": 0}