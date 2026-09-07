from django.conf import settings
from django.db import models


class Mission(models.Model):
    STATUT_CHOICES = [
        ("planifiee", "Planifiée"),
        ("en_cours", "En cours"),
        ("terminee", "Terminée"),
    ]

    date_depart = models.DateField()
    date_retour = models.DateField()
    lieu = models.CharField(max_length=255)
    motif = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="planifiee")

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="missions_creees",
    )

    def __str__(self):
        return f"{self.motif} — {self.lieu} ({self.date_depart})"