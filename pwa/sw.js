const CACHE_NAME = "stk-v1";
self.addEventListener("install", (e) => {
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(clients.claim());
});
// Do not intercept navigation requests - let the browser handle them normally
self.addEventListener("fetch", (e) => {
  // Only handle non-navigation requests for cached assets
  if (e.request.mode === "navigate") return;
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request))
  );
});
