<template>
  <div class="admin-page" v-loading="loading">
    <h2>⚙️ 管理后台</h2>
    <el-tabs>
      <el-tab-pane label="待审核点子">
        <el-table :data="pendingIdeas" stripe>
          <el-table-column prop="title" label="标题" show-overflow-tooltip />
          <el-table-column prop="author" label="作者" width="100" />
          <el-table-column prop="category" label="分类" width="80" />
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button type="success" size="small" @click="review(row.id, 'approve')">通过</el-button>
              <el-popconfirm title="确定拒绝？" @confirm="review(row.id, 'reject')">
                <template #reference><el-button type="danger" size="small">拒绝</el-button></template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="数据统计">
        <el-row :gutter="16">
          <el-col :span="6" v-for="s in statsCards" :key="s.label">
            <el-card><h3>{{ s.value }}</h3><p>{{ s.label }}</p></el-card>
          </el-col>
        </el-row>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '../api/request';

const loading = ref(true);
const pendingIdeas = ref([]);
const stats = ref({});

const statsCards = [
  { label: '用户总数', value: 0 }, { label: '热点总数', value: 0 },
  { label: '推荐总数', value: 0 }, { label: '企划总数', value: 0 }, { label: '点子总数', value: 0 },
];

async function load() {
  try {
    const [ideasRes, statsRes] = await Promise.allSettled([
      request.get('/admin/ideas/pending'),
      request.get('/admin/stats'),
    ]);
    if (ideasRes.status === 'fulfilled') pendingIdeas.value = ideasRes.value.items || [];
    if (statsRes.status === 'fulfilled') {
      stats.value = statsRes.value || {};
      statsCards[0].value = stats.value.users_total || 0;
      statsCards[1].value = stats.value.topics_total || 0;
      statsCards[2].value = stats.value.recommendations_total || 0;
      statsCards[3].value = stats.value.plans_total || 0;
      statsCards[4].value = stats.value.ideas_total || 0;
    }
  } finally { loading.value = false; }
}

async function review(ideaId, action) {
  await request.post(`/admin/ideas/${ideaId}/review?action=${action}`);
  load();
}

onMounted(load);
</script>

<style scoped>
.admin-page { max-width: 900px; margin: 0 auto; }
</style>
