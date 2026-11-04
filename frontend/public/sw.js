/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 * KOSHA LABS — Progressive Web App Service Worker
 * 
 * SECURITY COMPLIANCE:
 * - Only caches immutable static application shell assets (CSS, JS, fonts, icons).
 * - STRICTLY DOES NOT CACHE: worker records, authentication tokens, fingerprint
 *   images, biometric templates, or any dynamic API requests.
 */

const CACHE_NAME = 'kosha-labs-shell-v1';

// Static App Shell assets to pre-cache for instant loading
const APP_SHELL_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/pwa-192x192.png',
  '/pwa-512x512.png',
  '/apple-touch-icon.png',
  '/favicon-64x64.png'
];

// Sensitive keywords and paths that MUST NEVER be stored in service worker cache
const SENSITIVE_URL_PATTERNS = [
  '/api/',
  '/auth/',
  'supabase',
  'worker',
  'fingerprint',
  'biometric',
  'embedding',
  'verify',
  'recognize',
  'register',
  'template',
  'session'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(APP_SHELL_ASSETS).catch((err) => {
        // Pre-caching non-fatal if offline during install
        console.warn('[ServiceWorker] Pre-cache skipped asset:', err);
      });
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing legacy cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = request.url.toLowerCase();

  // 1. Non-GET requests (POST, PUT, DELETE) are never cached
  if (request.method !== 'GET') {
    return;
  }

  // 2. Security Check: Never intercept or cache sensitive worker, auth, or biometric endpoints
  const isSensitive = SENSITIVE_URL_PATTERNS.some((pattern) => url.includes(pattern));
  if (isSensitive) {
    // Network-only passthrough for all API and biometric calls
    return;
  }

  // 3. For navigation requests (loading pages/routes), use Network-first with Cache fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => {
        return caches.match('/index.html');
      })
    );
    return;
  }

  // 4. Stale-While-Revalidate for immutable static assets (JS, CSS, images, fonts)
  if (
    url.includes('/assets/') ||
    url.endsWith('.js') ||
    url.endsWith('.css') ||
    url.endsWith('.png') ||
    url.endsWith('.woff2') ||
    url.endsWith('.svg')
  ) {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        const fetchPromise = fetch(request).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseToCache);
            });
          }
          return networkResponse;
        }).catch(() => cachedResponse);

        return cachedResponse || fetchPromise;
      })
    );
  }
});
