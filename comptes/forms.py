from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Utilisateur


class InscriptionForm(UserCreationForm):
    role = forms.ChoiceField(choices=Utilisateur.ROLE_CHOICES, label="Rôle")

    class Meta:
        model = Utilisateur
        fields = ["last_name", "first_name", "username", "role", "password1", "password2"]
        labels = {
            "last_name": "Nom",
            "first_name": "Prénom",
            "username": "Matricule / Identifiant",
        }

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.statut_acces = "en_attente"
        if commit:
            utilisateur.save()
        return utilisateur
    
    
class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ["last_name", "first_name", "email"]
        labels = {
            "last_name": "Nom",
            "first_name": "Prénom",
            "email": "Adresse e-mail",
        }
        widgets = {
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }