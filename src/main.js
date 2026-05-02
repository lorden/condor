import { createApp } from 'vue';
import App from './App.vue';
import './styles.css';

// Apply persisted theme synchronously so the page doesn't flash.
try {
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') {
    document.documentElement.dataset.theme = stored === 'light' ? 'light' : '';
  }
} catch (_) { /* no-op */ }
// Debug log: main.js loaded
console.log('main.js loaded');

try {
  // Debug log: attempting to import Vue
  console.log('Importing Vue and App.vue...');
  // Debug log: attempting to mount Vue app
  console.log('Mounting Vue app...');
  createApp(App).mount('#app');
  // Debug log: Vue app mounted
  console.log('Vue app mounted');
} catch (e) {
  // Debug log: error occurred
  console.error('Error in main.js:', e);
}
