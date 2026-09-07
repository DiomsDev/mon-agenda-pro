from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("agenda/", views.agenda, name="agenda"),
    path("activites/", views.activites, name="activites"),
    path("missions/", views.missions, name="missions"),
    path("rendez-vous/", views.rendez_vous, name="rendez_vous"),
    path("reunions/", views.reunions, name="reunions"),
    path("visiteurs/", views.visiteurs, name="visiteurs"),
    path("contacts/", views.contacts, name="contacts"),
    path("taches/", views.taches, name="taches"),
    path("rappels/", views.rappels, name="rappels"),
    path("notifications/", views.notifications, name="notifications"),
    path("comptes-rendus/", views.comptes_rendus, name="comptes_rendus"),
    path("documents/", views.documents, name="documents"),
    path("statistiques/", views.statistiques, name="statistiques"),
    path("historique/", views.historique, name="historique"),
    path("assistants/", views.assistants, name="assistants"),
    path("parametres/", views.parametres, name="parametres"),
    path("activites/nouvelle/",views.nouvelle_activite,name="nouvelle_activite"),
    path("activites/<int:pk>/modifier/", views.modifier_activite, name="modifier_activite"),
    path("activites/<int:pk>/supprimer/", views.supprimer_activite, name="supprimer_activite"),
    path("missions/nouvelle/", views.nouvelle_mission, name="nouvelle_mission"),
    path("missions/<int:pk>/modifier/", views.modifier_mission, name="modifier_mission"),
    path("missions/<int:pk>/supprimer/", views.supprimer_mission, name="supprimer_mission"),
    path("rendez-vous/nouveau/", views.nouveau_rendez_vous, name="nouveau_rendez_vous"),
    path("rendez-vous/<int:pk>/modifier/", views.modifier_rendez_vous, name="modifier_rendez_vous"),
    path("rendez-vous/<int:pk>/supprimer/", views.supprimer_rendez_vous, name="supprimer_rendez_vous"),
]