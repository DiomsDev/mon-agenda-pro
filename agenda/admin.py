from django.contrib import admin
from .models import Activite


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ("objet", "date", "heure_debut", "lieu", "statut", "cree_par", "valide_par")
    list_filter = ("statut", "date")
    search_fields = ("objet", "lieu", "contact")