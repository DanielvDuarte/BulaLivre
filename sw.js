/* BulaLivre — Service Worker
   Permite usar o app offline após a primeira visita.
   - App shell (html, ícones, manifesto): cache-first.
   - bulas.json: network-first (pega a versão mais nova quando há internet,
     cai no cache quando offline). Assim o botão "Atualizar" sempre traz o
     dado mais recente, mas sem internet continua funcionando. */
const VERSION = "bulalivre-v4";
const SHELL = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icon-180.png",
  "./icon-192.png",
  "./icon-512.png",
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(VERSION).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // bulas.json -> network-first
  if (url.pathname.endsWith("/bulas.json") || url.pathname.endsWith("bulas.json")) {
    e.respondWith(
      fetch(req, { cache: "no-store" }).then((res) => {
        const copy = res.clone();
        caches.open(VERSION).then((c) => c.put("./bulas.json", copy));
        return res;
      }).catch(() => caches.match("./bulas.json"))
    );
    return;
  }

  // demais recursos -> cache-first, com atualização em segundo plano
  e.respondWith(
    caches.match(req).then((cached) => {
      const net = fetch(req).then((res) => {
        if (res && res.status === 200 && res.type === "basic") {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => cached);
      return cached || net;
    })
  );
});
