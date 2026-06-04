<template>
  <div class="recommend-page" v-loading="loading">
    <div class="page-header">
      <div>
        <h2>📋 个性化选题推荐</h2>
        <p class="desc">基于你的创作偏好，为你精选以下热点选题</p>
      </div>
      <div class="header-actions">
        <el-button round @click="load">🔄 换一批</el-button>
        <el-button type="primary" round @click="prefDialog = true">⚙️ 设置偏好</el-button>
      </div>
    </div>

    <!-- 推荐概览 -->
    <div class="overview-row" v-if="items.length">
      <div class="overview-card">
        <div class="overview-icon" style="background: linear-gradient(135deg, #6366f1, #818cf8);">📋</div>
        <div class="overview-info">
          <div class="overview-value">{{ items.length }}</div>
          <div class="overview-label">推荐选题</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon" style="background: linear-gradient(135deg, #10b981, #34d399);">👍</div>
        <div class="overview-info">
          <div class="overview-value">{{ likedCount }}</div>
          <div class="overview-label">已感兴趣</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon" style="background: linear-gradient(135deg, #f59e0b, #fbbf24);">🎯</div>
        <div class="overview-info">
          <div class="overview-value">{{ avgScore }}</div>
          <div class="overview-label">平均匹配分</div>
        </div>
      </div>
      <div class="overview-card">
        <div class="overview-icon" style="background: linear-gradient(135deg, #ec4899, #f472b6);">📊</div>
        <div class="overview-info">
          <div class="overview-value">{{ topCategories.length }}</div>
          <div class="overview-label">覆盖领域</div>
        </div>
      </div>
    </div>

    <!-- 三栏布局 -->
    <div class="rec-layout">
      <!-- 左侧主区域 -->
      <div class="rec-main">
        <el-empty v-if="!items.length && !loading" description="暂无推荐，请先在个人中心设置创作偏好" />

        <div class="card-grid">
          <div v-for="item in items" :key="item.id" class="rec-card" :class="{ liked: item.feedback === 'liked', disliked: item.feedback === 'disliked' }">
            <div class="card-score">
              <span class="score-value">{{ Math.round(item.score) }}</span>
              <span class="score-label">匹配分</span>
            </div>
            <h3 class="card-title">{{ item.topic_title }}</h3>
            <div class="card-tags">
              <el-tag v-for="tag in item.match_tags" :key="tag" size="small" type="primary" effect="plain" round>{{ tag }}</el-tag>
            </div>
            <p class="card-reason">💡 {{ item.reason }}</p>

            <!-- 创作难度评估 -->
            <div class="difficulty-bar">
              <span class="diff-label">创作难度</span>
              <div class="diff-track">
                <div class="diff-fill" :style="{ width: getDifficulty(item) + '%', background: getDiffColor(getDifficulty(item)) }"></div>
              </div>
              <span class="diff-text">{{ getDiffLabel(getDifficulty(item)) }}</span>
            </div>

            <!-- 预估数据 -->
            <div class="estimate-row">
              <div class="estimate-item">
                <span class="estimate-icon">👁️</span>
                <span class="estimate-val">{{ estimateViews(item) }}</span>
                <span class="estimate-desc">预估播放</span>
              </div>
              <div class="estimate-item">
                <span class="estimate-icon">🔥</span>
                <span class="estimate-val">{{ estimateHeat(item) }}</span>
                <span class="estimate-desc">预估热度</span>
              </div>
              <div class="estimate-item">
                <span class="estimate-icon">⏱</span>
                <span class="estimate-val">{{ estimateTime(item) }}</span>
                <span class="estimate-desc">制作耗时</span>
              </div>
            </div>

            <div class="card-actions">
              <el-button :type="item.feedback === 'liked' ? 'success' : 'default'" size="small" round @click="feedback(item, 'liked')">
                👍 感兴趣
              </el-button>
              <el-button :type="item.feedback === 'disliked' ? 'danger' : 'default'" size="small" round @click="feedback(item, 'disliked')">
                👎 不感兴趣
              </el-button>
              <el-button size="small" round @click="goPlan(item)">📝 生成企划</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧边栏 -->
      <div class="rec-sidebar">
        <!-- 热门领域排行 -->
        <div class="sidebar-card">
          <div class="sidebar-title">🔥 热门领域排行</div>
          <div class="rank-list">
            <div v-for="(cat, i) in topCategories" :key="cat.name" class="rank-item">
              <span class="rank-num" :class="'rank-' + Math.min(i + 1, 3)">{{ i + 1 }}</span>
              <div class="rank-info">
                <div class="rank-header">
                  <span class="rank-name">{{ categoryIcon(cat.name) }} {{ cat.name }}</span>
                  <span class="rank-count">{{ cat.count }}个推荐</span>
                </div>
                <div class="rank-bar-track">
                  <div class="rank-bar-fill" :style="{ width: cat.percent + '%' }"></div>
                </div>
              </div>
            </div>
            <div v-if="!topCategories.length" class="no-data">暂无数据</div>
          </div>
        </div>

        <!-- 创作灵感 -->
        <div class="sidebar-card">
          <div class="sidebar-title">✨ 创作灵感</div>
          <div class="inspiration-list">
            <div v-for="(tip, i) in inspirations" :key="i" class="inspiration-item">
              <span class="inspiration-num">{{ i + 1 }}</span>
              <div class="inspiration-content">
                <span class="inspiration-title">{{ tip.title }}</span>
                <span class="inspiration-desc">{{ tip.desc }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 推荐策略 -->
        <div class="sidebar-card">
          <div class="sidebar-title">🧠 推荐策略</div>
          <div class="strategy-list">
            <div v-for="s in strategies" :key="s.label" class="strategy-item" :class="{ active: s.active }">
              <span class="strategy-icon">{{ s.icon }}</span>
              <div class="strategy-info">
                <span class="strategy-label">{{ s.label }}</span>
                <span class="strategy-desc">{{ s.desc }}</span>
              </div>
              <el-switch v-model="s.active" size="small" />
            </div>
          </div>
        </div>

        <!-- 反馈历史 -->
        <div class="sidebar-card" v-if="historyItems.length">
          <div class="sidebar-title" style="justify-content: space-between;">
            <span style="display: flex; align-items: center; gap: 8px;">📊 反馈历史</span>
            <el-button size="small" text @click="historyItems = []">清空</el-button>
          </div>
          <div class="history-list">
            <div v-for="h in historyItems.slice(0, 8)" :key="h.id" class="history-item">
              <span class="history-title">{{ h.topic_title }}</span>
              <el-tag :type="h.feedback === 'liked' ? 'success' : 'danger'" size="small" effect="dark" round>
                {{ h.feedback === 'liked' ? '感兴趣' : '不感兴趣' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 偏好设置对话框 -->
    <el-dialog v-model="prefDialog" title="推荐偏好设置" width="500px">
      <el-form label-position="top">
        <el-form-item label="感兴趣的领域（可多选）">
          <el-checkbox-group v-model="prefInterests">
            <el-checkbox v-for="cat in allCategories" :key="cat" :label="cat">
              <span>{{ categoryIcon(cat) }} {{ cat }}</span>
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="创作风格偏好">
          <el-select v-model="prefStyle" multiple placeholder="选择风格" style="width: 100%">
            <el-option label="知识科普" value="知识科普" />
            <el-option label="新闻评论" value="新闻评论" />
            <el-option label="生活教程" value="生活教程" />
            <el-option label="搞笑段子" value="搞笑段子" />
            <el-option label="深度分析" value="深度分析" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="prefDialog = false" round>取消</el-button>
        <el-button type="primary" @click="savePref" round>保存并刷新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const router = useRouter();
const items = ref([]);
const loading = ref(true);
const historyItems = ref(JSON.parse(localStorage.getItem('rec_history') || '[]'));
const prefDialog = ref(false);
const allCategories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];
const prefInterests = ref([]);
const prefStyle = ref([]);

const strategies = ref([
  { label: '热度优先', desc: '优先推荐高热度话题', icon: '🔥', active: true },
  { label: '匹配优先', desc: '优先推荐与偏好匹配的', icon: '🎯', active: true },
  { label: '低竞争优先', desc: '优先推荐竞争度较低的', icon: '💎', active: false },
  { label: '时效优先', desc: '优先推荐最新话题', icon: '⏰', active: false },
]);

const inspirations = [
  { title: '跨界混搭', desc: '把科技和美食结合，做出差异化内容' },
  { title: '反转叙事', desc: '从反面角度解读热点，制造惊喜感' },
  { title: '数据可视化', desc: '用图表和数据说话，提升可信度' },
  { title: '个人故事', desc: '结合自身经历，增加情感共鸣' },
  { title: '系列连载', desc: '把大话题拆分成系列，提高粉丝粘性' },
];

function categoryIcon(cat) {
  const icons = { '时政': '🏛️', '财经': '💹', '科技': '🔬', '娱乐': '🎬', '体育': '⚽', '美食': '🍜', '教育': '📚', '其他': '📌' };
  return icons[cat] || '📌';
}

const likedCount = computed(() => items.value.filter(i => i.feedback === 'liked').length);
const avgScore = computed(() => {
  if (!items.value.length) return 0;
  return Math.round(items.value.reduce((s, i) => s + (i.score || 0), 0) / items.value.length);
});

// 热门领域排行
const topCategories = computed(() => {
  const map = {};
  items.value.forEach(item => {
    const tags = item.match_tags || [];
    tags.forEach(tag => { map[tag] = (map[tag] || 0) + 1; });
  });
  const total = items.value.length || 1;
  return Object.entries(map)
    .map(([name, count]) => ({ name, count, percent: Math.round((count / total) * 100) }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);
});

// 创作难度评估
function getDifficulty(item) {
  const score = item.score || 50;
  return Math.round(100 - score * 0.6 + Math.random() * 15);
}
function getDiffColor(val) {
  if (val < 30) return '#10b981';
  if (val < 60) return '#f59e0b';
  return '#ef4444';
}
function getDiffLabel(val) {
  if (val < 30) return '简单';
  if (val < 60) return '中等';
  return '较难';
}

// 预估数据
function estimateViews(item) {
  const base = (item.score || 50) * 100;
  return base > 10000 ? Math.round(base / 10000) + 'w' : base;
}
function estimateHeat(item) {
  return Math.round((item.score || 50) * 0.8) + '%';
}
function estimateTime(item) {
  const d = getDifficulty(item);
  if (d < 30) return '2-4h';
  if (d < 60) return '4-8h';
  return '1-2天';
}

async function load() {
  loading.value = true;
  try {
    const res = await request.get('/recommend');
    items.value = res.items || [];
  } finally { loading.value = false; }
}

async function feedback(item, type) {
  try {
    await request.post('/recommend/feedback', { recommend_id: item.id, feedback: type });
    item.feedback = type;
    historyItems.value.unshift({
      id: item.id, topic_title: item.topic_title, feedback: type,
      time: new Date().toLocaleString('zh-CN'),
    });
    if (historyItems.value.length > 50) historyItems.value = historyItems.value.slice(0, 50);
    localStorage.setItem('rec_history', JSON.stringify(historyItems.value));
  } catch {}
}

function goPlan(item) {
  router.push({ path: '/plan', query: { topic_title: item.topic_title } });
}

async function savePref() {
  try {
    for (const cat of prefInterests.value) {
      await request.post('/user/interests', { category: cat }).catch(() => {});
    }
  } catch {}
  ElMessage.success('偏好已更新，正在刷新推荐');
  prefDialog.value = false;
  load();
}

onMounted(load);
</script>

<style scoped>
.recommend-page { width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; }
.desc { color: var(--text-secondary); margin-top: 4px; font-size: 14px; }
.header-actions { display: flex; gap: 8px; }

/* Overview */
.overview-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.overview-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  display: flex; align-items: center; gap: 16px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all .2s;
}
.overview-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.overview-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
}
.overview-value { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.overview-label { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }

/* Layout */
.rec-layout { display: grid; grid-template-columns: 1fr 320px; gap: 20px; }
.rec-main { min-width: 0; }
.rec-sidebar { display: flex; flex-direction: column; gap: 16px; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 16px;
}

.rec-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 24px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  position: relative;
  transition: all .25s;
}
.rec-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}
.rec-card.liked { border-color: #10b981; }
.rec-card.disliked { border-color: #ef4444; opacity: .6; }

.card-score {
  position: absolute; top: 16px; right: 16px;
  background: linear-gradient(135deg, #6366f1, #a78bfa);
  color: #fff;
  padding: 8px 14px;
  border-radius: 12px;
  text-align: center;
}
.score-value { display: block; font-size: 20px; font-weight: 700; line-height: 1; }
.score-label { font-size: 10px; opacity: .8; }

.card-title {
  font-size: 17px; font-weight: 600;
  margin: 8px 60px 12px 0;
  line-height: 1.4;
}
.card-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.card-reason { font-size: 14px; line-height: 1.6; color: var(--text-secondary); margin-bottom: 14px; }

/* Difficulty */
.difficulty-bar {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 14px; font-size: 13px;
}
.diff-label { color: var(--text-secondary); flex-shrink: 0; }
.diff-track { flex: 1; height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.diff-fill { height: 100%; border-radius: 3px; transition: width .4s; }
.diff-text { font-weight: 600; min-width: 30px; }

/* Estimate */
.estimate-row {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;
  margin-bottom: 14px; padding: 12px;
  background: #f8fafc; border-radius: var(--radius-sm);
}
.estimate-item {
  display: flex; flex-direction: column; align-items: center; gap: 2px;
  text-align: center;
}
.estimate-icon { font-size: 16px; }
.estimate-val { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.estimate-desc { font-size: 11px; color: var(--text-secondary); }

.card-actions { display: flex; gap: 8px; flex-wrap: wrap; }

/* Sidebar */
.sidebar-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
.sidebar-title {
  font-size: 15px; font-weight: 600; margin-bottom: 14px;
  display: flex; align-items: center; gap: 8px;
}

/* Category Rank */
.rank-list { display: flex; flex-direction: column; gap: 12px; }
.rank-item { display: flex; gap: 10px; align-items: flex-start; }
.rank-num {
  width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; background: #f1f5f9; color: var(--text-secondary); flex-shrink: 0;
}
.rank-1 { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #fff; }
.rank-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #fff; }
.rank-3 { background: linear-gradient(135deg, #d97706, #f59e0b); color: #fff; }
.rank-info { flex: 1; }
.rank-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; }
.rank-name { font-weight: 600; }
.rank-count { color: var(--text-secondary); }
.rank-bar-track { height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.rank-bar-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #a78bfa); border-radius: 3px; transition: width .5s; }
.no-data { text-align: center; padding: 12px 0; color: var(--text-secondary); font-size: 13px; }

/* Inspiration */
.inspiration-list { display: flex; flex-direction: column; gap: 10px; }
.inspiration-item { display: flex; gap: 10px; }
.inspiration-num {
  width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
  background: #eef2ff; color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
}
.inspiration-content { display: flex; flex-direction: column; gap: 2px; }
.inspiration-title { font-size: 14px; font-weight: 600; }
.inspiration-desc { font-size: 12px; color: var(--text-secondary); }

/* Strategy */
.strategy-list { display: flex; flex-direction: column; gap: 10px; }
.strategy-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px; border-radius: var(--radius-sm);
  background: #f8fafc; transition: all .2s;
}
.strategy-item.active { background: #eef2ff; }
.strategy-icon { font-size: 18px; }
.strategy-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.strategy-label { font-size: 13px; font-weight: 600; }
.strategy-desc { font-size: 11px; color: var(--text-secondary); }

/* History */
.history-list { display: flex; flex-direction: column; gap: 2px; }
.history-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 0; border-bottom: 1px solid #f1f5f9;
  font-size: 13px;
}
.history-item:last-child { border-bottom: none; }
.history-title { flex: 1; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-right: 8px; }
</style>