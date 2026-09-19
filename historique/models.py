from django.conf import settings
from django.db import models


class HistoriqueAction(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="actions_historique",
    )
    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="actions",
    )
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.action} — {self.utilisateur} ({self.date:%d/%m/%Y %H:%M})"


class Notification(models.Model):
    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    message = models.CharField(max_length=255)
    lien = models.CharField(max_length=255, blank=True)
    lue = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.message} → {self.destinataire}"


class Rappel(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rappels",
    )
    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rappels",
    )
    titre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date_rappel = models.DateTimeField()
    termine = models.BooleanField(default=False)

    class Meta:
        ordering = ["date_rappel"]

    def __str__(self):
        return f"{self.titre} ({self.date_rappel:%d/%m/%Y %H:%M})"