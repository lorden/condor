import { createApp } from 'vue';
import App from './App.vue';
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
