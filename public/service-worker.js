const CACHE_NAME = "inventario-cache-v3";
const DYNAMIC_CACHE = "inventario-dynamic-v3";

const urlsToCache = [
  "./",
  "./index.html",
  "./app.js",
  "./manifest.json",
  "./quagga.min.js",
  "./xlsx.full.min.js",
  "./icon-192.png",
  "./icon-512.png"
];

// --------------------
// INSTALL
// --------------------
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
  self.skipWaiting();
});

// --------------------
// ACTIVATE
// --------------------
self.addEventListener("activate", event => {
  event.waitUntil(
    Promise.all([
      caches.keys().then(cacheNames =>
        Promise.all(
          cacheNames.map(cache => {
            if (cache !== CACHE_NAME && cache !== DYNAMIC_CACHE) {
              return caches.delete(cache);
            }
          })
        )
      ),
      self.clients.claim()
    ])
  );
});

// --------------------
// FETCH
// --------------------
self.addEventListener("fetch", event => {

  const requestUrl = new URL(event.request.url);

  // 🔥 JSON críticos → Network First
  if (
    requestUrl.pathname.includes("equivalencias.json") ||
    requestUrl.pathname.includes("referencias_sin_codigo_barras.json")
  ) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then(cache => {
            cache.put(event.request, responseClone);
          });
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // 📦 Resto de archivos → Cache First
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});