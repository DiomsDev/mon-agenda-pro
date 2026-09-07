from django.contrib import admin
from .models import Mission


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("motif", "lieu", "date_depart", "date_retour", "statut", "cree_par")
    list_filter = ("statut",)
    search_fields = ("motif", "lieu")