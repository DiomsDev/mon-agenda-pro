from django.core.management.base import BaseCommand

from entreprises.models import Entreprise
from historique.utils import verifier_rappels


class Command(BaseCommand):

    help = "Vérifie les rappels et crée les notifications."

    def handle(self, *args, **options):

        entreprises = Entreprise.objects.all()

        nombre = 0

        for entreprise in entreprises:

            verifier_rappels(entreprise)

            nombre += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Vérification des rappels effectuée pour "
                f"{nombre} entreprise(s)."
            )
        )