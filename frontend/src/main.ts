import { createApp } from 'vue';
import globalAxios from 'axios';
import { createPinia } from 'pinia';
import defineInterceptors from '@/config/axios';

import App from './App.vue';
import router from './router';

import '@/assets/styles/base.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.mount('#app');

defineInterceptors(globalAxios);
