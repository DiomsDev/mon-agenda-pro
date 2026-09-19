from django.contrib import admin
from .models import HistoriqueAction, Notification, Rappel


@admin.register(HistoriqueAction)
class HistoriqueActionAdmin(admin.ModelAdmin):
    list_display = ("action", "utilisateur", "entreprise", "date")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("message", "destinataire", "entreprise", "lue", "date")


@admin.register(Rappel)
class RappelAdmin(admin.ModelAdmin):
    list_display = ("titre", "utilisateur", "date_rappel", "termine")