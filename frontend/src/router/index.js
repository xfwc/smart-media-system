import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../store/auth';

const routes = [
  { path: '/', redirect: '/hot' },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { guest: true },
  },
  {
    path: '/hot',
    name: 'HotList',
    component: () => import('../views/HotList.vue'),
  },
  {
    path: '/hot/:id',
    name: 'TopicDetail',
    component: () => import('../views/TopicDetail.vue'),
  },
  {
    path: '/recommend',
    name: 'Recommend',
    component: () => import('../views/Recommend.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/plan',
    name: 'PlanGenerator',
    component: () => import('../views/PlanGenerator.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/ideas',
    name: 'IdeaHub',
    component: () => import('../views/IdeaHub.vue'),
  },
  {
    path: '/ideas/create',
    name: 'IdeaCreate',
    component: () => import('../views/IdeaCreate.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/ideas/:id',
    name: 'IdeaDetail',
    component: () => import('../views/IdeaDetail.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: () => import('../views/AdminPanel.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  if (to.meta.guest && authStore.isLoggedIn) {
    return next('/hot');
  }
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return next('/login');
  }
  if (to.meta.requiresAdmin && authStore.user?.role === 'creator') {
    return next('/hot');
  }
  next();
});

export default router;
