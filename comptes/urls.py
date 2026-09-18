from django.urls import path
from . import views

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('inscription/creer-entreprise/', views.creer_entreprise, name='creer_entreprise'),
    path('inscription/rejoindre-entreprise/', views.rejoindre_entreprise, name='rejoindre_entreprise'),
    path('profil/', views.modifier_profil, name='modifier_profil'),
    path('acces/', views.gestion_acces, name='gestion_acces'),
    path('acces/<int:pk>/rattacher/', views.rattacher_assistant, name='rattacher_assistant'),
    path('acces/<int:pk>/basculer/', views.basculer_acces, name='basculer_acces'),
]