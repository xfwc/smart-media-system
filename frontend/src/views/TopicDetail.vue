<template>
  <div class="topic-detail" v-loading="loading">
    <el-button text @click="$router.back()">← 返回热榜</el-button>

    <div class="title-row">
      <h2>{{ topic?.title }}</h2>
      <div class="keywords" v-if="analysis?.keywords?.length">
        <el-tag v-for="kw in analysis.keywords" :key="kw" type="success" effect="plain" size="small">{{ kw }}</el-tag>
      </div>
    </div>

    <div class="meta">
      <span>🔥 {{ formatHeat(topic?.heat_value) }}</span>
      <el-tag :type="topic?.rank <= 3 ? 'danger' : 'info'">热点排名 #{{ topic?.rank }}</el-tag>
      <el-tag>{{ topic?.category || '未分类' }}</el-tag>
      <el-tag v-if="topic?.risk_level" :type="sensitiveType(topic?.risk_level)">话题敏感度: {{ sensitiveHint(topic?.risk_level) }}</el-tag>
    </div>

    <div class="summary-box" v-if="topic?.summary">
      <h3>📰 事件概述</h3>
      <p>{{ topic.summary }}</p>
    </div>

    <div class="detail-box" v-if="topic?.detail_text">
      <h3>📋 完整事件描述</h3>
      <p>{{ topic.detail_text }}</p>
    </div>

    <el-button type="primary" size="large" @click="goGenerate" style="margin-top: 24px">📝 生成内容企划</el-button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import request from '../api/request';

const route = useRoute();
const router = useRouter();
const topic = ref(null);
const analysis = ref(null);
const loading = ref(true);

async function load() {
  try {
    const [topicRes, analysisRes] = await Promise.allSettled([
      request.get(`/hot/${route.params.id}`),
      request.get(`/hot/${route.params.id}/analysis`),
    ]);
    if (topicRes.status === 'fulfilled') topic.value = topicRes.value;
    if (analysisRes.status === 'fulfilled') analysis.value = analysisRes.value;
  } finally {
    loading.value = false;
  }
}

function formatHeat(val) { return val > 10000 ? Math.round(val / 10000) + 'w' : val; }

function sensitiveHint(level) {
  const map = { low: '客观陈述即可', medium: '建议理智发言', high: '注意谨慎发表观点' };
  return map[level] || level;
}
function sensitiveType(level) {
  return level === 'high' ? 'danger' : level === 'medium' ? 'warning' : 'success';
}
function goGenerate() {
  router.push({ path: '/plan', query: { topic_id: topic.value?.id } });
}
onMounted(load);
</script>

<style scoped>
.topic-detail { max-width: 800px; margin: 0 auto; }
.title-row { display: flex; align-items: center; gap: 16px; margin: 16px 0 8px; }
.title-row h2 { margin: 0; white-space: nowrap; }
.keywords { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.meta { display: flex; gap: 12px; align-items: center; margin-bottom: 20px; }
.summary-box { padding: 20px; background: #f0f7ff; border-left: 4px solid #409eff; border-radius: 4px; margin-bottom: 16px; }
.summary-box h3 { margin-bottom: 8px; font-size: 15px; }
.summary-box p { font-size: 14px; line-height: 1.8; color: #303133; }
.detail-box { padding: 20px; background: #fafafa; border: 1px solid #e4e7ed; border-radius: 4px; }
.detail-box h3 { margin-bottom: 12px; font-size: 15px; }
.detail-box p { font-size: 14px; line-height: 2; color: #303133; text-indent: 2em; }
</style>
