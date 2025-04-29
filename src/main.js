import { createApp } from 'vue';
import App from './App.vue';
import 'normalize.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './assets/style.css';
import './jswebrtc.min.js';

const app = createApp(App);
app.mount('#app'); 