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
    path("verifier-rappels-automatique/", views.verifier_rappels_automatique, name="verifier_rappels_automatique"),
    path("notifications/non-lues/",views.notifications_non_lues_api,name="notifications_non_lues_api"),

    # =========================================================
    # ACTIVITÉS — CRUD
    # =========================================================

    path(
        "activites/nouvelle/",
        views.nouvelle_activite,
        name="nouvelle_activite"
    ),

    path(
        "activites/<int:pk>/modifier/",
        views.modifier_activite,
        name="modifier_activite"
    ),

    path(
        "activites/<int:pk>/supprimer/",
        views.supprimer_activite,
        name="supprimer_activite"
    ),

    # =========================================================
    # MISSIONS — CRUD
    # =========================================================

    path(
        "missions/nouvelle/",
        views.nouvelle_mission,
        name="nouvelle_mission"
    ),

    path(
        "missions/<int:pk>/modifier/",
        views.modifier_mission,
        name="modifier_mission"
    ),

    path(
        "missions/<int:pk>/supprimer/",
        views.supprimer_mission,
        name="supprimer_mission"
    ),

    # =========================================================
    # RENDEZ-VOUS — CRUD
    # =========================================================

    path(
        "rendez-vous/nouveau/",
        views.nouveau_rendez_vous,
        name="nouveau_rendez_vous"
    ),

    path(
        "rendez-vous/<int:pk>/modifier/",
        views.modifier_rendez_vous,
        name="modifier_rendez_vous"
    ),

    path(
        "rendez-vous/<int:pk>/supprimer/",
        views.supprimer_rendez_vous,
        name="supprimer_rendez_vous"
    ),

    # =========================================================
    # RÉUNIONS — CRUD
    # =========================================================

    path(
        "reunions/nouvelle/",
        views.nouvelle_reunion,
        name="nouvelle_reunion"
    ),

    path(
        "reunions/<int:pk>/modifier/",
        views.modifier_reunion,
        name="modifier_reunion"
    ),

    path(
        "reunions/<int:pk>/supprimer/",
        views.supprimer_reunion,
        name="supprimer_reunion"
    ),
    
    



         # COMPTES RENDUS
        path(
              "reunions/<int:pk>/compte-rendu/",
               views.nouveau_compte_rendu,
               name="nouveau_compte_rendu"
        ),
       path(
             "comptes-rendus/<int:pk>/modifier/",
              views.modifier_compte_rendu,
              name="modifier_compte_rendu"
        ),
        path(
              "comptes-rendus/<int:pk>/voir/",
              views.voir_compte_rendu,
              name="voir_compte_rendu"
        ),


    

    # =========================================================
    # ARCHIVES
    # =========================================================

    path(
        "archives/",
        views.archives,
        name="archives"
    ),

    # =========================================================
    # EXPORTS
    # =========================================================

    path(
        "activites/<int:pk>/pdf/",
        views.activite_pdf,
        name="activite_pdf"
    ),

    path(
        "activites/<int:pk>/word/",
        views.activite_word,
        name="activite_word"
    ),

    path(
        "missions/<int:pk>/pdf/",
        views.mission_pdf,
        name="mission_pdf"
    ),

    path(
        "missions/<int:pk>/word/",
        views.mission_word,
        name="mission_word"
    ),

    path(
        "rendez-vous/<int:pk>/pdf/",
        views.rendez_vous_pdf,
        name="rendez_vous_pdf"
    ),

    path(
        "rendez-vous/<int:pk>/word/",
        views.rendez_vous_word,
        name="rendez_vous_word"
    ),

    # =========================================================
    # STATISTIQUES
    # =========================================================

    path(
        "statistiques/data/",
        views.statistiques_data,
        name="statistiques_data"
    ),
    
    
    path(
        "taches/nouveau/",
        views.nouvelle_tache,
        name="nouvelle_tache"
    ),
    
    
    
        # =========================================================
    # WEB PUSH — NOTIFICATIONS
    # =========================================================

    path(
        "push/public-key/",
        views.push_public_key,
        name="push_public_key"
    ),

    path(
        "push/subscribe/",
        views.push_subscribe,
        name="push_subscribe"
    ),
    
]