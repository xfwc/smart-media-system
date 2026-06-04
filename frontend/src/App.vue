<template>
  <div id="app" :class="{ 'no-sidebar': isAuthPage }">
    <!-- 侧边栏 -->
    <aside v-if="!isAuthPage" class="app-sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">S</div>
        <span class="logo-text">智能传媒</span>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/hot" class="nav-item" :class="{ active: isActive('/hot') }">
          <span class="nav-icon">🔥</span>
          <span class="nav-label">热榜分析</span>
        </router-link>
        <router-link to="/plan" class="nav-item" :class="{ active: isActive('/plan') }">
          <span class="nav-icon">📝</span>
          <span class="nav-label">内容企划</span>
        </router-link>
        <router-link to="/ideas" class="nav-item" :class="{ active: isActive('/ideas') }">
          <span class="nav-icon">💡</span>
          <span class="nav-label">点子库</span>
        </router-link>
        <router-link to="/recommend" class="nav-item" :class="{ active: isActive('/recommend') }">
          <span class="nav-icon">📋</span>
          <span class="nav-label">选题推荐</span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-item" :class="{ active: isActive('/admin') }">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">管理后台</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-version">v1.0.0</div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="app-main">
      <!-- 顶栏 -->
      <header v-if="!isAuthPage" class="app-topbar">
        <div class="topbar-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="topbar-right">
          <template v-if="authStore.isLoggedIn">
            <el-dropdown trigger="click">
              <div class="user-avatar">
                <el-avatar :size="34" class="avatar-circle">
                  {{ authStore.user?.username?.charAt(0)?.toUpperCase() }}
                </el-avatar>
                <span class="user-name">{{ authStore.user?.username }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/profile')">
                    <span>👤</span> 个人中心
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">
                    <span>🚪</span> 退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button text @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" round @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from './store/auth';

const route = useRoute();
const authStore = useAuthStore();

const isAuthPage = computed(() => ['/login', '/register'].includes(route.path));
const isAdmin = computed(() => authStore.user?.role === 'admin' || authStore.user?.role === 'superadmin');

const pageTitle = computed(() => {
  const map = {
    '/hot': '热榜分析',
    '/plan': '内容企划',
    '/ideas': '点子库',
    '/ideas/create': '发布点子',
    '/recommend': '选题推荐',
    '/profile': '个人中心',
    '/admin': '管理后台',
  };
  if (route.path.startsWith('/hot/')) return '话题详情';
  if (route.path.startsWith('/ideas/') && route.path !== '/ideas/create') return '点子详情';
  return map[route.path] || '智能传媒';
});

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/');
}

function handleLogout() {
  authStore.logout();
  window.location.href = '/login';
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --sidebar-width: 220px;
  --topbar-height: 60px;
  --primary: #6366f1;
  --primary-light: #818cf8;
  --primary-dark: #4f46e5;
  --bg-sidebar: #1e1b4b;
  --bg-sidebar-hover: #312e81;
  --bg-sidebar-active: #3730a3;
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-sidebar: #c7d2fe;
  --text-sidebar-active: #ffffff;
  --border-color: #e2e8f0;
  --shadow-sm: 0 1px 2px rgba(0,0,0,.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,.1), 0 2px 4px -2px rgba(0,0,0,.1);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,.1), 0 4px 6px -4px rgba(0,0,0,.1);
  --radius: 12px;
  --radius-sm: 8px;
}

html, body { height: 100%; width: 100%; overflow: hidden; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--bg-page);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

/* === Layout === */
#app { display: flex; height: 100vh; width: 100%; }
#app.no-sidebar { display: block; height: 100vh; }

/* === Sidebar === */
.app-sidebar {
  width: var(--sidebar-width);
  background: linear-gradient(180deg, var(--bg-sidebar) 0%, #0f0a2e 100%);
  color: var(--text-sidebar);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0; left: 0; bottom: 0;
  z-index: 100;
  box-shadow: 4px 0 24px rgba(0,0,0,.15);
}
.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(255,255,255,.08);
}
.logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--primary) 0%, #a78bfa 100%);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 18px; color: #fff;
}
.logo-text { font-size: 18px; font-weight: 700; color: #fff; letter-spacing: -.3px; }

.sidebar-nav { flex: 1; padding: 16px 12px; display: flex; flex-direction: column; gap: 4px; }
.nav-item {
  display: flex; align-items: center; gap: 12px;
  padding: 11px 16px;
  border-radius: var(--radius-sm);
  color: var(--text-sidebar);
  text-decoration: none;
  font-size: 14px; font-weight: 500;
  transition: all .2s;
}
.nav-item:hover { background: var(--bg-sidebar-hover); color: #fff; }
.nav-item.active {
  background: var(--bg-sidebar-active);
  color: var(--text-sidebar-active);
  box-shadow: 0 0 0 1px rgba(99,102,241,.3);
}
.nav-icon { font-size: 18px; width: 24px; text-align: center; }
.nav-label { white-space: nowrap; }

.sidebar-footer { padding: 16px 24px; border-top: 1px solid rgba(255,255,255,.08); }
.sidebar-version { font-size: 12px; color: rgba(255,255,255,.3); }

/* === Main Area === */
.app-main {
  flex: 1;
  margin-left: var(--sidebar-width);
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow-y: auto;
}
#app.no-sidebar .app-main { margin-left: 0; }

/* === Topbar === */
.app-topbar {
  height: var(--topbar-height);
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: var(--shadow-sm);
}
.page-title { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.user-avatar {
  display: flex; align-items: center; gap: 10px;
  cursor: pointer; padding: 4px 12px 4px 4px;
  border-radius: 24px;
  transition: background .2s;
}
.user-avatar:hover { background: #f1f5f9; }
.avatar-circle {
  background: linear-gradient(135deg, var(--primary) 0%, #a78bfa 100%) !important;
  color: #fff !important; font-weight: 600 !important;
}
.user-name { font-size: 14px; font-weight: 500; color: var(--text-primary); }

/* === Content === */
.app-content {
  flex: 1;
  padding: 28px 32px;
}

/* === Global Element Plus Overrides === */
.el-card {
  border-radius: var(--radius) !important;
  border: 1px solid var(--border-color) !important;
  box-shadow: var(--shadow-sm) !important;
  transition: box-shadow .25s, transform .25s !important;
}
.el-card:hover { box-shadow: var(--shadow-md) !important; }
.el-button--primary {
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%) !important;
  border: none !important;
  font-weight: 500 !important;
  color: #1e293b !important;
}
.el-button--primary:hover {
  background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary) 100%) !important;
  color: #0f172a !important;
}
.el-tag { border-radius: 6px !important; }
.el-input__wrapper, .el-textarea__inner {
  border-radius: var(--radius-sm) !important;
}
.el-table { border-radius: var(--radius) !important; overflow: hidden; }
.el-table th.el-table__cell { background: #f8fafc !important; color: var(--text-secondary) !important; font-weight: 600 !important; }
.el-descriptions { border-radius: var(--radius-sm) !important; overflow: hidden; }

/* === Scrollbar === */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* === Page shared === */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; }
.filters { display: flex; gap: 8px; margin-bottom: 20px; align-items: center; flex-wrap: wrap; }
</style>
