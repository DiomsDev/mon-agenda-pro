from django.urls import path
from . import views

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('acces/', views.gestion_acces, name='gestion_acces'),
    path('acces/<int:pk>/rattacher/', views.rattacher_assistant, name='rattacher_assistant'),
    path('acces/<int:pk>/basculer/', views.basculer_acces, name='basculer_acces'),
    path('profil/', views.modifier_profil, name='modifier_profil'),
]