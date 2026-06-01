<template>
  <div class="profile-page" v-loading="loading">
    <h2>个人中心</h2>
    <el-card style="max-width: 600px; margin: 0 auto">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ profile?.username }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ profile?.email || '未设置' }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ profile?.role || 'creator' === 'admin' ? '管理员' : '创作者' }}</el-descriptions-item>
      </el-descriptions>
      <h3 style="margin: 24px 0 12px">创作领域偏好</h3>
      <div class="categories">
        <el-checkbox-group v-model="selectedInterests">
          <el-checkbox v-for="cat in allCategories" :key="cat" :label="cat">{{ cat }}</el-checkbox>
        </el-checkbox-group>
      </div>
      <el-button type="primary" @click="saveInterests" style="margin-top: 16px">保存偏好</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '../api/request';

const profile = ref(null);
const loading = ref(true);
const selectedInterests = ref([]);
const allCategories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];

async function load() {
  try {
    const res = await request.get('/auth/me');
    profile.value = res.data;
    selectedInterests.value = res.data.interests || [];
  } finally { loading.value = false; }
}

async function saveInterests() {
  // Remove all, then add selected
  const current = profile.value?.interests || [];
  for (const cat of current) {
    await request.delete(`/user/interests/${cat}`).catch(() => {});
  }
  for (const cat of selectedInterests.value) {
    await request.post('/user/interests', { category: cat }).catch(() => {});
  }
  ElMessage.success('偏好已保存');
  load();
}

import { ElMessage } from 'element-plus';
onMounted(load);
</script>

<style scoped>
.profile-page { max-width: 800px; margin: 0 auto; }
.categories { display: flex; flex-wrap: wrap; gap: 8px; }
</style>
