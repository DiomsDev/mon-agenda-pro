from django import forms
from .models import Mission


class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        fields = ["motif", "lieu", "date_depart", "date_retour", "statut"]
        widgets = {
            "motif": forms.TextInput(attrs={"class": "form-control"}),
            "lieu": forms.TextInput(attrs={"class": "form-control"}),
            "date_depart": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "date_retour": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "statut": forms.Select(attrs={"class": "form-control"}),
        }