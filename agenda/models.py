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
    
    RAPPEL_CHOICES = [
        ("", "Aucun rappel"),
        ("15", "15 minutes avant"),
        ("30", "30 minutes avant"),
        ("60", "1 heure avant"),
        ("1440", "1 jour avant"),
    ]
    rappel_minutes_avant = models.CharField(max_length=10, choices=RAPPEL_CHOICES, blank=True)
    rappel_envoye = models.BooleanField(default=False)

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activites_creees",
    )
    
    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="activites",
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
    
    RAPPEL_CHOICES = [
        ("", "Aucun rappel"),
        ("15", "15 minutes avant"),
        ("30", "30 minutes avant"),
        ("60", "1 heure avant"),
        ("1440", "1 jour avant"),
    ]
    rappel_minutes_avant = models.CharField(max_length=10, choices=RAPPEL_CHOICES, blank=True)
    rappel_envoye = models.BooleanField(default=False)

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rendezvous_crees",
    )
    
    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="rendez_vous",
    )

    def __str__(self):
        return f"{self.objet} - {self.date}"


# =========================================================
# RÉUNIONS
# =========================================================

class Reunion(models.Model):
    STATUT_CHOICES = [
        ("planifiee", "Planifiée"),
        ("en_cours", "En cours"),
        ("terminee", "Terminée"),
        ("annulee", "Annulée"),
    ]

    titre = models.CharField(max_length=255)
    date = models.DateField()
    heure_debut = models.TimeField(null=True, blank=True)
    heure_fin = models.TimeField(null=True, blank=True)
    lieu = models.CharField(max_length=255, blank=True)

    organisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reunions_organisees",
    )

    participants = models.TextField(
        blank=True,
        help_text="Indiquez les participants à la réunion."
    )

    ordre_du_jour = models.TextField(blank=True)

    description = models.TextField(blank=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="planifiee"
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reunions_creees",
    )

    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="reunions",
    )

    def __str__(self):
        return f"{self.titre} - {self.date}"
    
    
    

# =========================================================
# COMPTES RENDUS DE RÉUNION
# =========================================================

class CompteRendu(models.Model):

    reunion = models.OneToOneField(
        Reunion,
        on_delete=models.CASCADE,
        related_name="compte_rendu",
    )

    date_redaction = models.DateField(
        auto_now_add=True
    )

    participants = models.TextField(
        blank=True,
        help_text="Participants présents à la réunion."
    )

    resume = models.TextField(
        blank=True,
        help_text="Résumé général de la réunion."
    )

    points_discutes = models.TextField(
        blank=True,
        help_text="Principaux points abordés pendant la réunion."
    )

    decisions = models.TextField(
        blank=True,
        help_text="Décisions prises pendant la réunion."
    )

    actions_a_realiser = models.TextField(
        blank=True,
        help_text="Actions ou tâches à réaliser après la réunion."
    )

    observations = models.TextField(
        blank=True,
        help_text="Observations ou informations complémentaires."
    )

    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comptes_rendus_crees",
    )

    entreprise = models.ForeignKey(
        "entreprises.Entreprise",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comptes_rendus",
    )

    def __str__(self):
        return f"Compte rendu - {self.reunion.titre}"

    