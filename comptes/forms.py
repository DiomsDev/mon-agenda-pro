from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Utilisateur

from entreprises.models import Entreprise


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
        
        




class CreerEntrepriseForm(UserCreationForm):
    nom_entreprise = forms.CharField(label="Nom de l'entreprise", max_length=255)

    class Meta:
        model = Utilisateur
        fields = ["last_name", "first_name", "username", "password1", "password2"]
        labels = {
            "last_name": "Nom",
            "first_name": "Prénom",
            "username": "Matricule / Identifiant",
        }

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        entreprise = Entreprise.objects.create(nom=self.cleaned_data["nom_entreprise"])
        utilisateur.entreprise = entreprise
        utilisateur.role = "directeur"
        utilisateur.statut_acces = "actif"
        if commit:
            utilisateur.save()
        return utilisateur


class RejoindreEntrepriseForm(UserCreationForm):
    entreprise = forms.ModelChoiceField(
        queryset=Entreprise.objects.filter(active=True), label="Entreprise"
    )
    role = forms.ChoiceField(choices=Utilisateur.ROLE_CHOICES, label="Rôle")

    class Meta:
        model = Utilisateur
        fields = ["last_name", "first_name", "username", "entreprise", "role", "password1", "password2"]
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