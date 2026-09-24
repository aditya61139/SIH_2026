// VoxSentinalX Minimal PWA Service Worker for Android WebAPK installation
const CACHE_NAME = 'voxsentinalx-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Pass-through to network for real-time WebSocket and API interactions
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
