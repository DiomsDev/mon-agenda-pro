from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur


class UtilisateurAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Informations DIRAGENDA", {"fields": ("role", "statut_acces", "directeur")}),
    )
    list_display = ("username", "get_full_name", "role", "statut_acces", "directeur")
    list_filter = ("role", "statut_acces")


admin.site.register(Utilisateur, UtilisateurAdmin)