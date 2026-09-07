from django.conf import settings
from django.db import models


# =========================================================
# ACTIVITÉS
# =========================================================

class Activite(models.Model):
    STATUT_CHOICES = [
        ("brouillon", "Brouillon"),
        ("en_attente", "En attente de validation"),
        ("confirmee", "Confirmée"),
        ("effectuee", "Effectuée"),
        ("annulee", "Annulée"),
    ]

    objet = models.CharField(max_length=255)
    date = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    heure_debut = models.TimeField(null=True, blank=True)
    heure_fin = models.TimeField(null=True, blank=True)
    lieu = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    observations = models.TextField(blank=True)
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="brouillon"
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activites_creees",
    )

    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activites_validees",
    )

    def __str__(self):
        return f"{self.objet} ({self.date})"


# =========================================================
# RENDEZ-VOUS
# =========================================================

class RendezVous(models.Model):
    STATUT_CHOICES = [
        ("planifie", "Planifié"),
        ("confirme", "Confirmé"),
        ("termine", "Terminé"),
        ("annule", "Annulé"),
    ]

    objet = models.CharField(max_length=255)
    date = models.DateField()
    heure = models.TimeField(null=True, blank=True)
    lieu = models.CharField(max_length=255, blank=True)
    personne = models.CharField(max_length=255, blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    observations = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="planifie"
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rendezvous_crees",
    )

    def __str__(self):
        return f"{self.objet} - {self.date}"


