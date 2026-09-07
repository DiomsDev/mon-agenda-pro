from django import forms
from .models import Activite
from .models import RendezVous


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
        ]

        widgets = {
            "objet": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Réunion avec le directeur",
            }),

            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),

            "date_fin": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),

            "heure_debut": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
            }),

            "heure_fin": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
            }),

            "lieu": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Salle de réunion",
            }),

            "contact": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nom, téléphone ou email",
            }),

            "observations": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Ajoutez des informations complémentaires...",
                "rows": 5,
            }),

            "statut": forms.Select(attrs={
                "class": "form-control",
            }),
        }




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
        ]

        widgets = {
            "objet": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Rencontre avec un partenaire",
            }),

            "date": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control",
            }),

            "heure": forms.TimeInput(attrs={
                "type": "time",
                "class": "form-control",
            }),

            "lieu": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Bureau du Directeur",
            }),

            "personne": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nom de la personne",
            }),

            "telephone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Numéro de téléphone",
            }),

            "observations": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Ajoutez des informations complémentaires...",
                "rows": 5,
            }),

            "statut": forms.Select(attrs={
                "class": "form-control",
            }),
        }      