<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <router-link to="/" class="logo">📊 智能传媒</router-link>
        <el-menu mode="horizontal" :default-active="activeMenu" router>
          <el-menu-item index="/hot">热榜分析</el-menu-item>
          <el-menu-item index="/plan">内容企划</el-menu-item>
          <el-menu-item index="/ideas">点子库</el-menu-item>
          <el-menu-item v-if="isAdmin" index="/admin">管理后台</el-menu-item>
        </el-menu>
        <div class="header-right">
          <template v-if="authStore.isLoggedIn">
            <el-dropdown>
              <span class="user-info">
                <el-avatar :size="32" icon="UserFilled" />
                {{ authStore.user?.username }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$router.push('/recommend')">选题推荐</el-dropdown-item>
                  <el-dropdown-item @click="$router.push('/profile')">个人中心</el-dropdown-item>
                  <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button text @click="$router.push('/login')">登录</el-button>
            <el-button type="primary" size="small" @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from './store/auth';

const route = useRoute();
const authStore = useAuthStore();

const activeMenu = computed(() => route.path);
const isAdmin = computed(() => authStore.user?.role === 'admin' || authStore.user?.role === 'superadmin');

function handleLogout() {
  authStore.logout();
  window.location.href = '/login';
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Helvetica Neue', Arial, sans-serif; background: #f5f7fa; }
.app-header {
  display: flex; align-items: center; background: #fff;
  border-bottom: 1px solid #e4e7ed; padding: 0 20px; height: 60px;
}
.logo { font-size: 18px; font-weight: bold; color: #409eff; text-decoration: none; margin-right: 30px; }
.header-right { margin-left: auto; display: flex; align-items: center; gap: 12px; }
.user-info { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.el-main { min-height: calc(100vh - 60px); padding: 20px; }
</style>
