from django.core.management.base import BaseCommand
from decouple import config
from comptes.models import Utilisateur


class Command(BaseCommand):
    help = "Crée ou met à jour un compte administrateur à partir des variables d'environnement"

    def handle(self, *args, **options):
        username = config('ADMIN_USERNAME', default='')
        password = config('ADMIN_PASSWORD', default='')
        email = config('ADMIN_EMAIL', default='')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_USERNAME ou ADMIN_PASSWORD non défini — commande ignorée."
            ))
            return

        utilisateur, cree = Utilisateur.objects.get_or_create(
            username=username,
            defaults={"email": email, "role": "directeur"},
        )
        utilisateur.set_password(password)
        utilisateur.is_superuser = True
        utilisateur.is_staff = True
        utilisateur.role = "directeur"
        utilisateur.statut_acces = "actif"
        utilisateur.save()

        if cree:
            self.stdout.write(self.style.SUCCESS(f"Compte admin '{username}' créé."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Compte admin '{username}' mis à jour."))