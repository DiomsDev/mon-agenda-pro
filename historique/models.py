from django.conf import settings
from django.db import models


class HistoriqueAction(models.Model):
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="actions_historique",
    )
    action = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.action} — {self.utilisateur} ({self.date:%d/%m/%Y %H:%M})"