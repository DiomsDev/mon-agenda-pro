const CACHE_NAME = "diragenda-v2";

// =========================================================
// INSTALLATION
// =========================================================

self.addEventListener("install", (event) => {
    self.skipWaiting();
});


// =========================================================
// ACTIVATION
// =========================================================

self.addEventListener("activate", (event) => {
    event.waitUntil(
        clients.claim()
    );
});


// =========================================================
// CACHE / MODE HORS LIGNE
// =========================================================

self.addEventListener("fetch", (event) => {

    // Ne traiter que les requêtes HTTP et HTTPS
    if (
        event.request.method !== "GET" ||
        !["http:", "https:"].includes(
            new URL(event.request.url).protocol
        )
    ) {
        return;
    }

    event.respondWith(
        fetch(event.request).catch(async () => {

            const reponseEnCache = await caches.match(
                event.request
            );

            if (reponseEnCache) {
                return reponseEnCache;
            }

            // Aucune réponse disponible hors ligne
            return new Response(
                "Cette ressource est indisponible hors ligne.",
                {
                    status: 503,
                    statusText: "Service Unavailable",
                    headers: {
                        "Content-Type": "text/plain; charset=utf-8"
                    }
                }
            );
        })
    );

});


// =========================================================
// NOTIFICATION PUSH
// =========================================================

self.addEventListener("push", (event) => {

    let donnees = {
        title: "DIRAGENDA",
        body: "Vous avez une nouvelle notification.",
        url: "/"
    };

    try {
        if (event.data) {
            donnees = event.data.json();
        }
    } catch (erreur) {
        console.error(
            "Erreur lors de la lecture de la notification Push :",
            erreur
        );
    }

    const options = {
        body: donnees.body,
        icon: "/static/images/icon-192.png",
        badge: "/static/images/icon-192.png",
        data: {
            url: donnees.url || "/"
        },
        vibrate: [200, 100, 200]
    };

    event.waitUntil(
        self.registration.showNotification(
            donnees.title || "DIRAGENDA",
            options
        )
    );
});


// =========================================================
// CLIC SUR LA NOTIFICATION
// =========================================================

self.addEventListener("notificationclick", (event) => {

    event.notification.close();

    const url = event.notification.data?.url || "/";

    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true
        }).then((fenetres) => {

            for (const fenetre of fenetres) {

                if ("focus" in fenetre) {
                    fenetre.navigate(url);
                    return fenetre.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});