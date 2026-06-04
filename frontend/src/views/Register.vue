<template>
  <div class="register-page">
    <div class="register-bg">
      <div class="bg-circle c1"></div>
      <div class="bg-circle c2"></div>
      <div class="bg-circle c3"></div>
    </div>
    <div class="register-card">
      <div class="card-header">
        <div class="brand">
          <div class="brand-icon">S</div>
          <span>智能传媒</span>
        </div>
        <h2>创建账号</h2>
        <p class="subtitle">注册后即可开始创作之旅</p>
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" size="large">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="3-50位字母/数字" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="选填" prefix-icon="Message" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少8位" prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password placeholder="再次输入密码" prefix-icon="Lock" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="handleRegister" style="width: 100%; height: 44px; font-size: 15px">
            注 册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="link-text">已有账号？<router-link to="/login">去登录</router-link></div>
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
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' });

const validateConfirm = (_rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次密码不一致'));
  else callback();
};

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在3-50之间', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
};

async function handleRegister() {
  loading.value = true;
  try {
    const res = await request.post('/auth/register', {
      username: form.username,
      password: form.password,
      email: form.email || undefined,
    });
    authStore.setAuth(res.token, { username: res.username, role: 'creator' });
    router.push('/profile');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
  position: relative;
  overflow: hidden;
}
.register-bg {
  position: absolute; inset: 0;
  pointer-events: none;
}
.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: .1;
}
.c1 { width: 500px; height: 500px; background: #818cf8; top: -150px; left: -80px; }
.c2 { width: 350px; height: 350px; background: #a78bfa; bottom: -80px; right: -60px; }
.c3 { width: 180px; height: 180px; background: #c4b5fd; bottom: 30%; left: 15%; }

.register-card {
  width: 440px;
  background: rgba(255,255,255,.97);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px 36px;
  box-shadow: 0 25px 50px rgba(0,0,0,.25);
  position: relative;
  z-index: 1;
}
.card-header { text-align: center; margin-bottom: 28px; }
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
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
