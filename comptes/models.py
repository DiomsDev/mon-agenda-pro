from django.contrib.auth.models import AbstractUser
from django.db import models


class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ("directeur", "Directeur"),
        ("assistant", "Assistant(e) de direction"),
    ]
    STATUT_ACCES_CHOICES = [
        ("actif", "Actif"),
        ("en_attente", "En attente d'activation"),
        ("inactif", "Inactif"),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    statut_acces = models.CharField(
        max_length=20, choices=STATUT_ACCES_CHOICES, default="en_attente"
    )
    directeur = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistants",
        limit_choices_to={"role": "directeur"},
    )

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        if not self.is_superuser:
            self.is_active = self.statut_acces == "actif"
        super().save(*args, **kwargs)