<template>
  <div class="topic-detail" v-loading="loading">
    <el-button text @click="$router.back()">← 返回热榜</el-button>
    <h2>{{ topic?.title }}</h2>
    <div class="meta">
      <el-tag :type="topic?.rank <= 3 ? 'danger' : 'info'">排名 #{{ topic?.rank }}</el-tag>
      <el-tag>{{ topic?.category || '未分类' }}</el-tag>
      <el-tag v-if="topic?.risk_level" :type="riskType(topic?.risk_level)">风险: {{ topic?.risk_level }}</el-tag>
      <span>热度: {{ topic?.heat_value?.toLocaleString() }}</span>
    </div>
    <div v-if="analysis" class="analysis-section">
      <h3>📊 热点分析</h3>
      <div class="keywords">
        <el-tag v-for="kw in analysis.keywords" :key="kw" type="success" effect="plain" style="margin: 4px">{{ kw }}</el-tag>
      </div>
      <el-descriptions :column="2" border style="margin-top: 16px">
        <el-descriptions-item label="情感倾向">
          <el-tag :type="sentimentType(analysis.sentiment)">{{ analysis.sentiment }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="风险评级">
          <el-tag :type="riskType(analysis.risk_level)">{{ analysis.risk_level }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
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
    if (topicRes.status === 'fulfilled') topic.value = topicRes.value.data;
    if (analysisRes.status === 'fulfilled') analysis.value = analysisRes.value.data;
  } finally {
    loading.value = false;
  }
}

function riskType(level) {
  return level === 'high' ? 'danger' : level === 'medium' ? 'warning' : 'success';
}
function sentimentType(s) {
  return s === 'positive' ? 'success' : s === 'negative' ? 'danger' : 'info';
}
function goGenerate() {
  router.push({ path: '/plan', query: { topic_id: topic.value?.id } });
}
onMounted(load);
</script>

<style scoped>
.topic-detail { max-width: 800px; margin: 0 auto; }
.topic-detail h2 { margin: 16px 0; }
.meta { display: flex; gap: 12px; align-items: center; margin: 16px 0; }
.analysis-section { margin-top: 24px; padding: 20px; background: #f8f9fa; border-radius: 8px; }
.keywords { margin: 12px 0; }
</style>
