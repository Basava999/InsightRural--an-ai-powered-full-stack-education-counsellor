// InsightRural Service Worker
// Enables offline functionality and caching

const CACHE_NAME = 'insightrural-v1.1';
const OFFLINE_URL = '/offline.html';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
    '/',
    '/index.html',
    '/offline.html',
    '/css/style.css',
    '/css/components/chat.css',
    '/css/components/sidebar.css',
    '/css/components/predictor.css',
    '/css/components/dashboard.css',
    '/js/app.js',
    '/js/components/chat.js',
    '/js/components/sidebar.js',
    '/js/components/predictor.js',
    '/js/components/voice.js',
    '/js/components/dashboard.js',
    '/js/components/documents.js',
    '/js/pwa.js',
    '/manifest.json',
    '/assets/icons/icon-192.png',
    '/assets/icons/icon-512.png'
];

// API endpoints to cache with network-first strategy
const API_CACHE_PATTERNS = [
    '/api/colleges',
    '/api/branches',
    '/api/locations',
    '/api/statistics'
];

// Install event - precache assets
self.addEventListener('install', (event) => {
    console.log('[SW] Installing Service Worker...');

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Precaching app shell...');
                return cache.addAll(PRECACHE_ASSETS.map(url => {
                    return new Request(url, { cache: 'reload' });
                })).catch(err => {
                    console.log('[SW] Precache failed for some assets:', err);
                });
            })
            .then(() => {
                console.log('[SW] Service Worker installed successfully');
                return self.skipWaiting();
            })
    );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating Service Worker...');

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames
                        .filter((name) => name !== CACHE_NAME)
                        .map((name) => {
                            console.log('[SW] Deleting old cache:', name);
                            return caches.delete(name);
                        })
                );
            })
            .then(() => {
                console.log('[SW] Service Worker activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // Skip chrome-extension and other non-http requests
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // API requests - network first, cache fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirst(request));
        return;
    }

    // Static assets - cache first, network fallback
    event.respondWith(cacheFirst(request));
});

// Cache-first strategy
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);

    if (cachedResponse) {
        // Return cached response, but update cache in background
        updateCache(request);
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('[SW] Fetch failed, returning offline page');
        return caches.match(OFFLINE_URL);
    }
}

// Network-first strategy
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;
    } catch (error) {
        console.log('[SW] Network failed, trying cache...');
        const cachedResponse = await caches.match(request);

        if (cachedResponse) {
            return cachedResponse;
        }

        // Return offline JSON for API requests
        return new Response(JSON.stringify({
            error: 'You are offline',
            offline: true
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

// Update cache in background
async function updateCache(request) {
    try {
        const networkResponse = await fetch(request);

        if (networkResponse.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse);
        }
    } catch (error) {
        // Silently fail - we already have cached version
    }
}

// Handle push notifications (for future use)
self.addEventListener('push', (event) => {
    if (!event.data) return;

    const data = event.data.json();

    const options = {
        body: data.body || 'New update from InsightRural',
        icon: '/assets/icons/icon-192.png',
        badge: '/assets/icons/badge-72.png',
        vibrate: [100, 50, 100],
        data: {
            url: data.url || '/'
        },
        actions: [
            { action: 'open', title: 'Open' },
            { action: 'close', title: 'Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'InsightRural', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    event.notification.close();

    if (event.action === 'close') return;

    const url = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window' }).then((clientList) => {
            // Focus existing window if available
            for (const client of clientList) {
                if (client.url === url && 'focus' in client) {
                    return client.focus();
                }
            }
            // Open new window
            if (clients.openWindow) {
                return clients.openWindow(url);
            }
        })
    );
});

// Background sync (for offline form submissions)
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-predictions') {
        event.waitUntil(syncPredictions());
    }
});

async function syncPredictions() {
    // Sync any offline predictions when back online
    console.log('[SW] Syncing offline predictions...');
}

console.log('[SW] Service Worker loaded');
