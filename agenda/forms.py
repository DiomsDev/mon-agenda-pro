from django import forms

from .models import (
    Activite,
    RendezVous,
    Reunion,
    CompteRendu,
    Tache,
)


# =========================================================
# FORMULAIRE ACTIVITÉ
# =========================================================

class ActiviteForm(forms.ModelForm):

    class Meta:
        model = Activite

        fields = [
            "objet",
            "date",
            "date_fin",
            "heure_debut",
            "heure_fin",
            "lieu",
            "contact",
            "observations",
            "statut",
            "rappel_minutes_avant",
        ]

        widgets = {
            "objet": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Réunion avec le directeur",
                }
            ),

            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "date_fin": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "heure_debut": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "heure_fin": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "lieu": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Salle de réunion",
                }
            ),

            "contact": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom, téléphone ou email",
                }
            ),

            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ajoutez des informations complémentaires...",
                    "rows": 5,
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "rappel_minutes_avant": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }


# =========================================================
# FORMULAIRE RENDEZ-VOUS
# =========================================================

class RendezVousForm(forms.ModelForm):

    class Meta:
        model = RendezVous

        fields = [
            "objet",
            "date",
            "heure",
            "lieu",
            "personne",
            "telephone",
            "observations",
            "statut",
            "rappel_minutes_avant",
        ]

        widgets = {
            "objet": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Rencontre avec un partenaire",
                }
            ),

            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "heure": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "lieu": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Bureau du Directeur",
                }
            ),

            "personne": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom de la personne",
                }
            ),

            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Numéro de téléphone",
                }
            ),

            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ajoutez des informations complémentaires...",
                    "rows": 5,
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "rappel_minutes_avant": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }


# =========================================================
# FORMULAIRE RÉUNION
# =========================================================

class ReunionForm(forms.ModelForm):

    class Meta:
        model = Reunion

        fields = [
            "titre",
            "date",
            "heure_debut",
            "heure_fin",
            "lieu",
            "organisateur",
            "participants",
            "ordre_du_jour",
            "description",
            "statut",
            "rappel_minutes_avant",
        ]

        widgets = {
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Réunion avec l'équipe",
                }
            ),

            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "heure_debut": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "heure_fin": forms.TimeInput(
                attrs={
                    "type": "time",
                    "class": "form-control",
                }
            ),

            "lieu": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Salle de réunion",
                }
            ),

            "organisateur": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "participants": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Indiquez les participants à la réunion...",
                    "rows": 4,
                }
            ),

            "ordre_du_jour": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Indiquez les points à traiter...",
                    "rows": 5,
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ajoutez des informations complémentaires...",
                    "rows": 5,
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "rappel_minutes_avant": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }


# =========================================================
# FORMULAIRE COMPTE RENDU
# =========================================================

class CompteRenduForm(forms.ModelForm):

    class Meta:
        model = CompteRendu

        fields = [
            "participants",
            "resume",
            "points_discutes",
            "decisions",
            "actions_a_realiser",
            "observations",
        ]

        widgets = {
            "participants": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Indiquez les participants présents à la réunion...",
                    "rows": 4,
                }
            ),

            "resume": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Présentez brièvement le déroulement et le contenu de la réunion...",
                    "rows": 5,
                }
            ),

            "points_discutes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Indiquez les principaux points abordés...",
                    "rows": 5,
                }
            ),

            "decisions": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Indiquez les décisions prises pendant la réunion...",
                    "rows": 5,
                }
            ),

            "actions_a_realiser": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Indiquez les actions ou tâches à réaliser après la réunion...",
                    "rows": 5,
                }
            ),

            "observations": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ajoutez des observations ou informations complémentaires...",
                    "rows": 5,
                }
            ),
        }
# =========================================================
# FORMULAIRE TÂCHE / TO-DO LIST
# =========================================================


class TacheForm(forms.ModelForm):

    class Meta:
        model = Tache

        fields = [
            "titre",
            "description",
            "date_echeance",
            "priorite",
            "statut",
            "responsable",
        ]

        widgets = {
            "titre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Préparer le rapport mensuel",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Décrivez la tâche à réaliser...",
                    "rows": 5,
                }
            ),

            "date_echeance": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),

            "priorite": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "responsable": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        responsables = kwargs.pop("responsables", None)

        super().__init__(*args, **kwargs)

        if responsables is not None:

            self.fields["responsable"].queryset = responsables

        self.fields["responsable"].required = False