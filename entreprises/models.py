from django.db import models


class Entreprise(models.Model):
    nom = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom