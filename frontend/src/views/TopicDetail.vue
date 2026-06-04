<template>
  <div class="topic-detail" v-loading="loading">
    <div class="back-btn" @click="$router.back()">
      <span class="back-arrow">←</span> 返回热榜
    </div>

    <!-- 主信息卡 -->
    <div class="main-card" v-if="topic">
      <div class="topic-header">
        <div class="rank-badge" :class="'rank-' + Math.min(topic.rank, 3)">#{{ topic.rank }}</div>
        <h1 class="topic-title">{{ topic.title }}</h1>
      </div>

      <div class="meta-tags">
        <span class="meta-item heat">
          <span class="meta-icon">🔥</span>
          {{ formatHeat(topic.heat_value) }} 热度
        </span>
        <el-tag effect="plain" round>{{ topic.category || '未分类' }}</el-tag>
        <el-tag v-if="topic.risk_level" :type="sensitiveType(topic.risk_level)" effect="dark" round>
          {{ sensitiveHint(topic.risk_level) }}
        </el-tag>
        <div style="margin-left: auto; display: flex; gap: 8px;">
          <el-button :type="isFavorite ? 'warning' : 'default'" size="small" round @click="toggleFavorite">
            {{ isFavorite ? '⭐ 已收藏' : '☆ 收藏' }}
          </el-button>
          <el-button size="small" round @click="shareTopic">🔗 分享</el-button>
        </div>
      </div>

      <div class="keywords" v-if="analysis?.keywords?.length">
        <span class="kw-label">关键词</span>
        <el-tag v-for="kw in analysis.keywords" :key="kw" type="primary" effect="plain" size="small" round>{{ kw }}</el-tag>
      </div>
    </div>

    <div class="content-layout" v-if="topic">
      <!-- 左侧主内容 -->
      <div class="left-col">
        <!-- 内容区域 -->
        <div class="summary-section" v-if="topic.summary">
          <div class="section-header">
            <span class="section-icon">📰</span>
            <h3>事件概述</h3>
          </div>
          <p>{{ topic.summary }}</p>
        </div>

        <div class="detail-section" v-if="topic.detail_text">
          <div class="section-header">
            <span class="section-icon">📋</span>
            <h3>完整描述</h3>
          </div>
          <p>{{ topic.detail_text }}</p>
        </div>

        <!-- 热度走势图 -->
        <div class="heat-trend-section">
          <div class="section-header">
            <span class="section-icon">📈</span>
            <h3>热度走势</h3>
          </div>
          <div class="trend-chart">
            <div class="trend-area">
              <svg width="100%" height="120" viewBox="0 0 400 120" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stop-color="#6366f1" stop-opacity="0.3"/>
                    <stop offset="100%" stop-color="#6366f1" stop-opacity="0"/>
                  </linearGradient>
                </defs>
                <path :d="trendAreaPath" fill="url(#trendGrad)" />
                <path :d="trendLinePath" fill="none" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle v-for="(p, i) in trendPoints" :key="i" :cx="p.x" :cy="p.y" r="3.5" fill="#6366f1" stroke="#fff" stroke-width="2"/>
              </svg>
            </div>
            <div class="trend-labels">
              <span v-for="(label, i) in trendLabels" :key="i">{{ label }}</span>
            </div>
          </div>
        </div>

        <!-- 评论区域 -->
        <div class="comment-section">
          <div class="section-header">
            <span class="section-icon">💬</span>
            <h3>话题讨论 ({{ comments.length }})</h3>
          </div>
          <div class="comment-input">
            <el-input v-model="commentText" placeholder="发表你的看法..." maxlength="500" show-word-limit>
              <template #append>
                <el-button type="primary" @click="submitComment">发布</el-button>
              </template>
            </el-input>
          </div>
          <div v-for="c in comments" :key="c.id" class="comment-item">
            <div class="comment-header">
              <div class="comment-author">
                <div class="comment-avatar">{{ c.author?.charAt(0) }}</div>
                <strong>{{ c.author }}</strong>
              </div>
              <span class="comment-time">{{ c.time }}</span>
            </div>
            <p class="comment-text">{{ c.content }}</p>
            <div class="comment-actions">
              <span class="comment-action" @click="c.liked = !c.liked">
                {{ c.liked ? '❤️' : '🤍' }} {{ c.likes }}
              </span>
            </div>
          </div>
          <div v-if="!comments.length" class="no-comments">
            <p>暂无评论，来发表第一条吧</p>
          </div>
        </div>
      </div>

      <!-- 右侧边栏 -->
      <div class="right-col">
        <!-- 操作区 -->
        <div class="action-card">
          <el-button type="primary" size="large" @click="goGenerate" round style="width: 100%">
            📝 生成内容企划
          </el-button>
          <el-button size="large" @click="goCreateIdea" round style="width: 100%">
            💡 基于此发布点子
          </el-button>
        </div>

        <!-- 相关推荐 -->
        <div class="related-section">
          <div class="section-header">
            <span class="section-icon">🔗</span>
            <h3>相关热点</h3>
          </div>
          <div v-for="r in relatedTopics" :key="r.id" class="related-item" @click="$router.push(`/hot/${r.id}`)">
            <span class="related-rank">#{{ r.rank }}</span>
            <div class="related-info">
              <span class="related-title">{{ r.title }}</span>
              <span class="related-meta">🔥 {{ formatHeat(r.heat_value) }} · {{ r.category }}</span>
            </div>
          </div>
          <div v-if="!relatedTopics.length" class="no-data">暂无相关热点</div>
        </div>

        <!-- AI 洞察 -->
        <div class="insight-section" v-if="analysis">
          <div class="section-header">
            <span class="section-icon">🤖</span>
            <h3>AI 洞察</h3>
          </div>
          <div class="insight-list">
            <div v-if="analysis.sentiment" class="insight-item">
              <span class="insight-label">情感倾向</span>
              <el-tag :type="analysis.sentiment === 'positive' ? 'success' : analysis.sentiment === 'negative' ? 'danger' : 'warning'" size="small" effect="dark" round>
                {{ analysis.sentiment === 'positive' ? '正面' : analysis.sentiment === 'negative' ? '负面' : '中性' }}
              </el-tag>
            </div>
            <div v-if="analysis.heat_prediction" class="insight-item">
              <span class="insight-label">热度预测</span>
              <span class="insight-value">{{ analysis.heat_prediction }}</span>
            </div>
            <div v-if="analysis.angle_suggestions?.length" class="insight-item vertical">
              <span class="insight-label">推荐创作角度</span>
              <div class="angle-tags">
                <el-tag v-for="a in analysis.angle_suggestions" :key="a" size="small" effect="plain" round>{{ a }}</el-tag>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分享对话框 -->
    <el-dialog v-model="shareDialog" title="分享话题" width="440px">
      <div class="share-content">
        <el-input :model-value="shareUrl" readonly>
          <template #append>
            <el-button @click="copyShareUrl">复制</el-button>
          </template>
        </el-input>
        <div class="share-channels">
          <div class="share-channel" @click="shareToChannel('wechat')">
            <div class="channel-icon" style="background: #07c160;">微</div>
            <span>微信</span>
          </div>
          <div class="share-channel" @click="shareToChannel('weibo')">
            <div class="channel-icon" style="background: #e6162d;">博</div>
            <span>微博</span>
          </div>
          <div class="share-channel" @click="shareToChannel('qq')">
            <div class="channel-icon" style="background: #12b7f5;">Q</div>
            <span>QQ</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const route = useRoute();
const router = useRouter();
const topic = ref(null);
const analysis = ref(null);
const loading = ref(true);
const commentText = ref('');
const shareDialog = ref(false);
const relatedTopics = ref([]);

// 收藏
const favorites = ref(JSON.parse(localStorage.getItem('hot_favorites') || '[]'));
const isFavorite = computed(() => topic.value ? favorites.value.includes(topic.value.id) : false);
function toggleFavorite() {
  if (!topic.value) return;
  const idx = favorites.value.indexOf(topic.value.id);
  if (idx >= 0) { favorites.value.splice(idx, 1); ElMessage.success('已取消收藏'); }
  else { favorites.value.push(topic.value.id); ElMessage.success('已收藏'); }
  localStorage.setItem('hot_favorites', JSON.stringify(favorites.value));
}

// 分享
const shareUrl = computed(() => window.location.href);
function shareTopic() { shareDialog.value = true; }
function copyShareUrl() {
  navigator.clipboard?.writeText(shareUrl.value);
  ElMessage.success('链接已复制');
}
function shareToChannel(ch) {
  ElMessage.success(`已分享到${ch === 'wechat' ? '微信' : ch === 'weibo' ? '微博' : 'QQ'}`);
  shareDialog.value = false;
}

// 评论（本地模拟）
const comments = ref([]);
function submitComment() {
  if (!commentText.value.trim()) return;
  comments.value.unshift({
    id: Date.now(), author: '我', content: commentText.value,
    time: new Date().toLocaleString('zh-CN'), likes: 0, liked: false,
  });
  commentText.value = '';
}

// 热度走势（模拟）
const trendPoints = computed(() => {
  const pts = [];
  const heat = topic.value?.heat_value || 1000;
  for (let i = 0; i < 7; i++) {
    pts.push({
      x: i * (400 / 6),
      y: 110 - ((Math.sin(i * 0.8 + 1) * 0.3 + 0.6) * 90 + Math.random() * 10),
    });
  }
  return pts;
});
const trendLinePath = computed(() => trendPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' '));
const trendAreaPath = computed(() => {
  const line = trendLinePath.value;
  const last = trendPoints.value[trendPoints.value.length - 1];
  const first = trendPoints.value[0];
  return `${line} L${last.x},120 L${first.x},120 Z`;
});
const trendLabels = ['7天前', '6天前', '5天前', '4天前', '3天前', '2天前', '昨天'];

async function load() {
  try {
    const [topicRes, analysisRes] = await Promise.allSettled([
      request.get(`/hot/${route.params.id}`),
      request.get(`/hot/${route.params.id}/analysis`),
    ]);
    if (topicRes.status === 'fulfilled') topic.value = topicRes.value;
    if (analysisRes.status === 'fulfilled') analysis.value = analysisRes.value;

    // 加载相关热点
    try {
      const listRes = await request.get('/hot/list', { params: { page_size: 6, category: topic.value?.category } });
      relatedTopics.value = (listRes.items || []).filter(i => i.id != route.params.id).slice(0, 5);
    } catch {}
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
function goCreateIdea() {
  router.push({ path: '/ideas/create', query: { topic_title: topic.value?.title } });
}
onMounted(load);
</script>

<style scoped>
.topic-detail { width: 100%; }

.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--primary); font-size: 14px; font-weight: 500;
  cursor: pointer; margin-bottom: 20px;
  padding: 6px 14px; border-radius: 8px;
  transition: background .2s;
}
.back-btn:hover { background: #eef2ff; }
.back-arrow { font-size: 18px; }

.main-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 28px 32px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  margin-bottom: 20px;
}
.topic-header { display: flex; align-items: flex-start; gap: 16px; margin-bottom: 16px; }
.rank-badge {
  flex-shrink: 0;
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700;
  background: #f1f5f9; color: var(--text-secondary);
}
.rank-1 { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #fff; }
.rank-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #fff; }
.rank-3 { background: linear-gradient(135deg, #d97706, #f59e0b); color: #fff; }

.topic-title { font-size: 22px; font-weight: 700; line-height: 1.4; }

.meta-tags { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }
.meta-item {
  display: flex; align-items: center; gap: 4px;
  font-size: 14px; font-weight: 500;
  padding: 4px 12px; border-radius: 20px;
  background: #fef3c7; color: #92400e;
}
.meta-icon { font-size: 16px; }

.keywords { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.kw-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; margin-right: 4px; }

/* Layout */
.content-layout { display: grid; grid-template-columns: 1fr 340px; gap: 20px; }
.left-col, .right-col { display: flex; flex-direction: column; gap: 16px; }

.summary-section, .detail-section, .heat-trend-section, .comment-section, .related-section, .insight-section, .action-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 24px 28px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
.summary-section { border-left: 4px solid var(--primary); }

.section-header {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 14px;
}
.section-icon { font-size: 20px; }
.section-header h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }

.summary-section p, .detail-section p {
  font-size: 15px; line-height: 1.9; color: var(--text-primary);
}
.detail-section p { text-indent: 2em; }

/* Trend chart */
.trend-area { margin-bottom: 4px; }
.trend-labels { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-secondary); }

/* Comments */
.comment-input { margin-bottom: 16px; }
.comment-item { padding: 14px 0; border-bottom: 1px solid #f1f5f9; }
.comment-item:last-child { border-bottom: none; }
.comment-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.comment-author { display: flex; align-items: center; gap: 8px; }
.comment-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; color: #fff;
}
.comment-time { font-size: 12px; color: #94a3b8; }
.comment-text { font-size: 14px; line-height: 1.7; color: var(--text-primary); }
.comment-actions { margin-top: 6px; }
.comment-action { font-size: 13px; cursor: pointer; }
.no-comments { text-align: center; padding: 20px 0; color: var(--text-secondary); font-size: 14px; }

/* Action card */
.action-card { display: flex; flex-direction: column; gap: 10px; }

/* Related */
.related-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 12px 0; border-bottom: 1px solid #f1f5f9;
  cursor: pointer; transition: all .15s;
}
.related-item:hover { padding-left: 6px; }
.related-item:last-child { border-bottom: none; }
.related-rank {
  flex-shrink: 0; font-size: 13px; font-weight: 700;
  color: var(--primary); min-width: 28px;
}
.related-info { display: flex; flex-direction: column; gap: 4px; }
.related-title { font-size: 14px; font-weight: 500; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.related-meta { font-size: 12px; color: var(--text-secondary); }
.no-data { text-align: center; padding: 20px 0; color: var(--text-secondary); font-size: 14px; }

/* Insight */
.insight-list { display: flex; flex-direction: column; gap: 12px; }
.insight-item { display: flex; align-items: center; justify-content: space-between; }
.insight-item.vertical { flex-direction: column; align-items: flex-start; gap: 8px; }
.insight-label { font-size: 13px; color: var(--text-secondary); }
.insight-value { font-size: 14px; font-weight: 600; color: var(--primary); }
.angle-tags { display: flex; flex-wrap: wrap; gap: 6px; }

/* Share dialog */
.share-content { display: flex; flex-direction: column; gap: 20px; }
.share-channels { display: flex; gap: 24px; justify-content: center; }
.share-channel { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; }
.channel-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 18px;
  transition: transform .2s;
}
.share-channel:hover .channel-icon { transform: scale(1.1); }
.share-channel span { font-size: 12px; color: var(--text-secondary); }
</style>
