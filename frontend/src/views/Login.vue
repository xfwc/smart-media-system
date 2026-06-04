<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
    </div>
    <div class="login-card">
      <div class="card-header">
        <div class="brand">
          <div class="brand-icon">S</div>
          <span>智能传媒</span>
        </div>
        <h2>欢迎回来</h2>
        <p class="subtitle">登录你的账号以继续</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleLogin" style="width: 100%; height: 44px; font-size: 15px">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="link-text">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import request from '../api/request';
import { useAuthStore } from '../store/auth';

const router = useRouter();
const authStore = useAuthStore();
const loading = ref(false);
const form = reactive({ username: '', password: '' });
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

async function handleLogin() {
  loading.value = true;
  try {
    const res = await request.post('/auth/login', form);
    authStore.setAuth(res.token, { username: res.username, role: res.role });
    router.push('/hot');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
  position: relative;
  overflow: hidden;
}
.login-bg {
  position: absolute; inset: 0;
  pointer-events: none;
}
.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: .12;
}
.c1 { width: 600px; height: 600px; background: #818cf8; top: -200px; right: -100px; }
.c2 { width: 400px; height: 400px; background: #a78bfa; bottom: -100px; left: -80px; }
.c3 { width: 200px; height: 200px; background: #c4b5fd; top: 50%; left: 20%; }

.login-card {
  width: 420px;
  background: rgba(255,255,255,.97);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px 36px;
  box-shadow: 0 25px 50px rgba(0,0,0,.25);
  position: relative;
  z-index: 1;
}
.card-header { text-align: center; margin-bottom: 32px; }
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.brand-icon {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #a78bfa 100%);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 20px; color: #fff;
}
.brand span { font-size: 20px; font-weight: 700; color: #1e293b; }
.card-header h2 { font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 6px; }
.subtitle { color: #64748b; font-size: 14px; }

.link-text { text-align: center; margin-top: 20px; color: #64748b; font-size: 14px; }
.link-text a { color: #6366f1; text-decoration: none; font-weight: 500; }
.link-text a:hover { text-decoration: underline; }
</style>
