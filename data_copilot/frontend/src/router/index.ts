import { createRouter, createWebHistory } from 'vue-router';

import Home from '@/pages/Home.vue';
import Login from '@/pages/Login.vue';
import Signup from '@/pages/Signup.vue';
import Chat from '@/pages/Chat.vue';
import ChatWelcomePage from '@/pages/ChatWelcomePage.vue';
import ServiceDown from '@/pages/ServiceDown.vue';
import NotFound from '@/pages/NotFound.vue';
// eslint-disable-next-line import/no-cycle
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      beforeEnter(to, from, next) {
        const authStore = useAuthStore();
        if (from.path === '/login') {
          authStore.activateAnimation = true;
        } else {
          authStore.activateAnimation = false;
        }

        next();
      },
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
      meta: {
        layout: 'Auth',
      },
    },
    {
      path: '/signup',
      name: 'signup',
      component: Signup,
      meta: {
        layout: 'Auth',
      },
    },
    {
      path: '/chat-welcome/:id',
      name: 'chat-welcome',
      component: ChatWelcomePage,
    },
    {
      path: '/chat/:id',
      name: 'chat/:id',
      component: Chat,
    },
    {
      path: '/service-down',
      name: 'service-down',
      component: ServiceDown,
      meta: {
        layout: 'Error',
      },
    },
    {
      path: '/not-found',
      name: 'not-found',
      component: NotFound,
    },
    {
      path: '/:pathMatch(.*)',
      name: 'not-found',
      component: NotFound,
    },
  ],
});

// eslint-disable-next-line consistent-return
router.beforeEach(async (to) => {
  // redirect to login page if not logged in and trying to access a restricted page
  const publicPages = ['/login', '/signup'];
  const authRequired = !publicPages.includes(to.path);
  const auth = useAuthStore();

  if (authRequired && !auth.accessToken) {
    return '/login';
  }
});

export default router;
