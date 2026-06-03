<template>
  <div class="recommend-page" v-loading="loading">
    <h2>📋 个性化选题推荐</h2>
    <p class="desc">基于你的创作偏好，为你推荐以下热点选题</p>
    <el-empty v-if="!items.length && !loading" description="暂无推荐，请先在个人中心设置创作偏好" />
    <div class="card-grid">
      <el-card v-for="item in items" :key="item.id" class="rec-card">
        <div class="score-badge">{{ Math.round(item.score) }}分</div>
        <h3>{{ item.topic_title }}</h3>
        <div class="tags">
          <el-tag v-for="tag in item.match_tags" :key="tag" size="small" type="success" effect="plain">{{ tag }}</el-tag>
        </div>
        <p class="reason">💡 {{ item.reason }}</p>
        <div class="actions">
          <el-button :type="item.feedback === 'liked' ? 'success' : 'default'" size="small" @click="feedback(item, 'liked')">👍 感兴趣</el-button>
          <el-button :type="item.feedback === 'disliked' ? 'danger' : 'default'" size="small" @click="feedback(item, 'disliked')">👎 不感兴趣</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '../api/request';

const items = ref([]);
const loading = ref(true);

async function load() {
  try {
    const res = await request.get('/recommend');
    items.value = res.items || [];
  } finally { loading.value = false; }
}

async function feedback(item, type) {
  try {
    await request.post('/recommend/feedback', { recommend_id: item.id, feedback: type });
    item.feedback = type;
  } catch {}
}

onMounted(load);
</script>

<style scoped>
.recommend-page { max-width: 900px; margin: 0 auto; }
.desc { color: #909399; margin-bottom: 20px; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }
.rec-card { position: relative; }
.score-badge { position: absolute; top: 12px; right: 12px; background: #409eff; color: #fff; padding: 4px 10px; border-radius: 12px; font-size: 14px; font-weight: bold; }
.rec-card h3 { font-size: 16px; margin: 8px 0; padding-right: 60px; }
.tags { display: flex; gap: 6px; margin: 8px 0; flex-wrap: wrap; }
.reason { color: #606266; font-size: 13px; margin: 8px 0; }
.actions { display: flex; gap: 8px; margin-top: 12px; }
</style>
