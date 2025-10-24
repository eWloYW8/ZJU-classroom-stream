import { createApp } from 'vue';
import App from './App.vue';
import 'normalize.css';
import '@fortawesome/fontawesome-free/css/all.min.css';
import './assets/style.css';

// 动态加载 jswebrtc
const script = document.createElement('script');
script.src = '/js/jswebrtc.min.js';
script.async = true;
document.head.appendChild(script);

const app = createApp(App);
app.mount('#app'); 