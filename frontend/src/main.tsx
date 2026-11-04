import {createRoot} from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Register PWA Service Worker for Offline Shell & Mobile Installation
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((reg) => {
        console.log('[Kosha PWA] Service worker registered successfully:', reg.scope);
      })
      .catch((err) => {
        console.warn('[Kosha PWA] Service worker registration failed:', err);
      });
  });
}

createRoot(document.getElementById('root')!).render(<App />);
