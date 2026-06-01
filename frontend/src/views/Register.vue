<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2>注册新账号</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="3-50位字母/数字" size="large" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="选填" size="large" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少8位" size="large" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" show-password size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleRegister" style="width: 100%">注册</el-button>
        </el-form-item>
      </el-form>
      <div class="link-text">已有账号？<router-link to="/login">去登录</router-link></div>
    </el-card>
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
    authStore.setAuth(res.data.token, { username: res.data.username, role: 'creator' });
    router.push('/profile');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.register-page { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.register-card { width: 420px; }
.register-card h2 { text-align: center; margin-bottom: 24px; }
.link-text { text-align: center; margin-top: 16px; color: #909399; }
</style>
