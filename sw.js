/* Service worker — keeps the app on the device so it opens and works with no reception.

   The page (index.html): served from the cache, so the app opens at once, with or without
   reception. The page asks for an update itself — {type:"check-update"} when it loads and
   whenever it comes back to the foreground (an installed iPad app is usually resumed, not
   reloaded). The worker then fetches index.html from the server; if it changed, the new copy
   goes into the cache and the page gets {type:"update-ready"} and shows a "new version" pill.
   A deploy therefore needs no version bump here.

   Other app files (manifest, icons): stale-while-revalidate.
   Google Fonts: cache-first, filled on the first open with reception.

   Bump SHELL only when ASSETS or the logic in this file changes — that makes the browser
   install this worker again and drop the old cache. */
"use strict";

const SHELL = "vasa-shell-v1";
const FONTS = "vasa-fonts-v1";
const ASSETS = [
  "./", "manifest.webmanifest",
  "icons/apple-touch-icon.png", "icons/icon-192.png", "icons/icon-512.png",
  "icons/icon-maskable-512.png", "icons/favicon-32.png"
];
const FONT_HOSTS = ["https://fonts.googleapis.com", "https://fonts.gstatic.com"];
/* the page itself — "./" and "index.html" are one cache entry */
const PAGE = new URL("./", self.registration.scope).href;

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL)
    .then(c => c.addAll(ASSETS.map(u => new Request(u, {cache: "reload"}))))
    .then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== SHELL && k !== FONTS).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (FONT_HOSTS.includes(url.origin)) { e.respondWith(cacheFirst(FONTS, req)); return; }
  if (url.origin !== self.location.origin) return;
  if (req.mode === "navigate" || url.href.split(/[?#]/)[0] === PAGE + "index.html") {
    e.respondWith(cacheFirst(SHELL, PAGE));
    return;
  }
  e.respondWith(staleWhileRevalidate(req, e));
});

self.addEventListener("message", e => {
  if (!e.data || e.data.type !== "check-update") return;
  e.waitUntil(checkPage()
    .then(changed => { if (changed && e.source) e.source.postMessage({type: "update-ready"}); })
    .catch(() => {}));
});

/* true when the server has a different index.html than the cached one (now replaced) */
async function checkPage() {
  const cache = await caches.open(SHELL);
  const [cached, res] = await Promise.all([cache.match(PAGE), fetch(PAGE, {cache: "no-cache"})]);
  if (!res.ok) return false;
  const now = await res.clone().text();
  const was = cached ? await cached.text() : null;
  if (was === now) return false;
  await cache.put(PAGE, res);
  return was !== null;
}

async function cacheFirst(name, req) {
  const cache = await caches.open(name);
  const hit = await cache.match(req, {ignoreSearch: name === SHELL});
  if (hit) return hit;
  const res = await fetch(req);
  /* the fonts stylesheet link has no crossorigin attribute, so its response is opaque — still cacheable */
  if (res.ok || res.type === "opaque") await cache.put(req, res.clone());
  return res;
}

async function staleWhileRevalidate(req, e) {
  const cache = await caches.open(SHELL);
  const cached = await cache.match(req, {ignoreSearch: true});
  const fresh = fetch(req, {cache: "no-cache"}).then(async res => {
    if (res.ok) await cache.put(req, res.clone());
    return res;
  });
  if (cached) { e.waitUntil(fresh.catch(() => {})); return cached; }
  return fresh;
}
