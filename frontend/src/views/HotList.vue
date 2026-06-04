<template>
  <div class="hot-page">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f97316, #fb923c);">🔥</div>
        <div class="stat-info">
          <div class="stat-value">{{ total }}</div>
          <div class="stat-label">热点总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #818cf8);">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ categories.length }}</div>
          <div class="stat-label">覆盖分类</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #34d399);">⏱</div>
        <div class="stat-info">
          <div class="stat-value">{{ autoRefresh ? countdown + 's' : '关闭' }}</div>
          <div class="stat-label">自动刷新</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #ec4899, #f472b6);">⭐</div>
        <div class="stat-info">
          <div class="stat-value">{{ favorites.length }}</div>
          <div class="stat-label">我的收藏</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #8b5cf6, #a78bfa);">🚀</div>
        <div class="stat-info">
          <div class="stat-value">{{ risingCount }}</div>
          <div class="stat-label">飙升热点</div>
        </div>
      </div>
    </div>

    <!-- 三栏布局 -->
    <div class="hot-layout">
      <!-- 左侧主区域 -->
      <div class="hot-main">
        <!-- 筛选栏 -->
        <el-card class="filter-card">
          <div class="filter-row">
            <el-input v-model="keyword" placeholder="搜索热点话题..." clearable @change="fetchList"
              style="width: 280px" prefix-icon="Search" />
            <div class="filter-right">
              <el-radio-group v-model="category" @change="fetchList" size="default">
                <el-radio-button value="">全部</el-radio-button>
                <el-radio-button v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</el-radio-button>
              </el-radio-group>
              <el-segmented v-model="sortBy" :options="sortOptions" @change="fetchList" />
              <el-tooltip content="仅看收藏">
                <el-button :type="showFavOnly ? 'warning' : 'default'" round @click="showFavOnly = !showFavOnly">
                  ⭐ {{ showFavOnly ? '已筛选' : '收藏' }}
                </el-button>
              </el-tooltip>
            </div>
          </div>
          <div class="filter-tools">
            <el-switch v-model="autoRefresh" active-text="自动刷新" inactive-text="" style="--el-switch-on-color: #10b981" />
            <el-button size="small" text @click="exportData">📥 导出数据</el-button>
            <el-button size="small" text @click="fetchList">🔄 手动刷新</el-button>
          </div>
        </el-card>

        <!-- 分类热度分布图 -->
        <el-card class="chart-card">
          <template #header>
            <div class="chart-header">
              <span class="chart-title">📈 分类热度分布</span>
              <el-radio-group v-model="chartMode" size="small">
                <el-radio-button value="bar">柱状图</el-radio-button>
                <el-radio-button value="pie">饼图</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" v-if="categoryStats.length">
            <div v-if="chartMode === 'bar'" class="bar-chart">
              <div v-for="cat in categoryStats" :key="cat.name" class="bar-item">
                <span class="bar-label">{{ cat.name }}</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: cat.percent + '%', background: cat.color }"></div>
                </div>
                <span class="bar-value">{{ cat.count }}</span>
              </div>
            </div>
            <div v-else class="pie-chart">
              <div class="pie-visual" :style="{ background: pieGradient }">
                <div class="pie-center">{{ total }}</div>
              </div>
              <div class="pie-legend">
                <div v-for="cat in categoryStats" :key="cat.name" class="legend-item">
                  <span class="legend-dot" :style="{ background: cat.color }"></span>
                  <span class="legend-name">{{ cat.name }}</span>
                  <span class="legend-val">{{ cat.count }} ({{ cat.percent }}%)</span>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无数据" :image-size="60" />
        </el-card>

        <!-- 列表 -->
        <el-card class="table-card" v-loading="loading">
          <el-table :data="filteredItems" @row-click="goDetail" style="cursor: pointer" :show-header="true">
            <el-table-column prop="rank" label="排名" width="80" align="center">
              <template #default="{ row }">
                <span class="rank-badge" :class="'rank-' + Math.min(row.rank, 3)">{{ row.rank }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="话题" min-width="400" show-overflow-tooltip>
              <template #default="{ row }">
                <div class="topic-cell">
                  <span class="topic-title">{{ row.title }}</span>
                  <span v-if="row.risk_level === 'high'" class="risk-dot"></span>
                  <span v-if="isFavorite(row.id)" class="fav-star">⭐</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="heat_value" label="热度" width="150" sortable>
              <template #default="{ row }">
                <div class="heat-cell">
                  <div class="heat-bar" :style="{ width: heatPercent(row.heat_value) + '%' }"></div>
                  <span class="heat-text">{{ formatHeat(row.heat_value) }}</span>
                  <span v-if="row.heat_trend === 'up'" class="trend-up">↑</span>
                  <span v-else-if="row.heat_trend === 'down'" class="trend-down">↓</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" round>{{ row.category || '其他' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="日期" width="110">
              <template #default="{ row }">
                <span class="date-text">{{ row.collected_at?.slice(5, 10) || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button :type="isFavorite(row.id) ? 'warning' : 'default'" size="small" circle
                  @click.stop="toggleFavorite(row)">
                  {{ isFavorite(row.id) ? '⭐' : '☆' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <div class="pagination-wrap">
            <el-pagination v-model:current-page="page" :total="showFavOnly ? favorites.length : total" :page-size="20"
              layout="prev, pager, next" @change="fetchList" />
          </div>
        </el-card>
      </div>

      <!-- 右侧边栏 -->
      <div class="hot-sidebar">
        <!-- 热搜词云 -->
        <div class="sidebar-card">
          <div class="sidebar-title">☁️ 热搜词云</div>
          <div class="word-cloud">
            <span v-for="word in hotWords" :key="word.text" class="cloud-word"
              :class="'tier-' + word.tier"
              :style="{ background: word.bg, color: word.color, borderColor: word.color }">
              {{ word.text }}
            </span>
          </div>
        </div>

        <!-- 飙升榜 -->
        <div class="sidebar-card">
          <div class="sidebar-title">🚀 飙升榜</div>
          <div class="rising-list">
            <div v-for="(item, i) in risingItems" :key="i" class="rising-item" @click="goDetail(item)">
              <span class="rising-rank" :class="'rising-' + Math.min(i + 1, 3)">{{ i + 1 }}</span>
              <div class="rising-info">
                <span class="rising-title">{{ item.title }}</span>
                <span class="rising-heat">🔥 {{ formatHeat(item.heat_value) }}</span>
              </div>
              <span class="rising-arrow">↑</span>
            </div>
          </div>
        </div>

        <!-- 实时动态 -->
        <div class="sidebar-card">
          <div class="sidebar-title">
            <span>📡 实时动态</span>
            <span class="live-dot"></span>
          </div>
          <div class="live-feed">
            <div v-for="(feed, i) in liveFeeds" :key="i" class="feed-item">
              <span class="feed-time">{{ feed.time }}</span>
              <span class="feed-text">{{ feed.text }}</span>
            </div>
          </div>
        </div>

        <!-- 风险预警 -->
        <div class="sidebar-card">
          <div class="sidebar-title">⚠️ 风险预警</div>
          <div class="risk-list">
            <div v-for="item in riskItems" :key="item.id" class="risk-item" @click="goDetail(item)">
              <span class="risk-icon" :class="'risk-' + (item.risk_level || 'low')">
                {{ item.risk_level === 'high' ? '🔴' : item.risk_level === 'medium' ? '🟡' : '🟢' }}
              </span>
              <span class="risk-title">{{ item.title }}</span>
            </div>
            <div v-if="!riskItems.length" class="no-risk">暂无风险热点</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const router = useRouter();
const items = ref([]);
const loading = ref(false);
const page = ref(1);
const total = ref(0);
const category = ref('');
const sortBy = ref('rank');
const keyword = ref('');
const showFavOnly = ref(false);
const autoRefresh = ref(false);
const countdown = ref(30);
const chartMode = ref('bar');
const categories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];
const sortOptions = [
  { label: '排名', value: 'rank' },
  { label: '热度', value: 'heat' },
  { label: '时间', value: 'time' },
];

const categoryColors = {
  '时政': '#ef4444', '财经': '#f59e0b', '科技': '#6366f1', '娱乐': '#ec4899',
  '体育': '#10b981', '美食': '#f97316', '教育': '#3b82f6', '其他': '#8b5cf6',
};

let maxHeat = 1;
let refreshTimer = null;
let feedTimer = null;

// 收藏功能
const favorites = ref(JSON.parse(localStorage.getItem('hot_favorites') || '[]'));

function isFavorite(id) { return favorites.value.includes(id); }
function toggleFavorite(row) {
  const idx = favorites.value.indexOf(row.id);
  if (idx >= 0) {
    favorites.value.splice(idx, 1);
    ElMessage.success('已取消收藏');
  } else {
    favorites.value.push(row.id);
    ElMessage.success('已收藏');
  }
  localStorage.setItem('hot_favorites', JSON.stringify(favorites.value));
}

const filteredItems = computed(() => {
  if (!showFavOnly.value) return items.value;
  return items.value.filter(i => favorites.value.includes(i.id));
});

// 飙升热点
const risingItems = computed(() => {
  return items.value.filter(i => i.heat_trend === 'up').slice(0, 8);
});
const risingCount = computed(() => risingItems.value.length);

// 风险热点
const riskItems = computed(() => {
  return items.value.filter(i => i.risk_level === 'high' || i.risk_level === 'medium').slice(0, 6);
});

// 热搜词云 — 三级等宽 tag 风格
const hotWords = computed(() => {
  const words = [];
  items.value.slice(0, 30).forEach(item => {
    const title = item.title || '';
    const parts = title.split(/[\s,，。！？、：；""''【】《》()（）\[\]]+/).filter(p => p.length >= 2);
    parts.forEach(p => {
      const existing = words.find(w => w.text === p);
      if (existing) { existing.weight += 1; }
      else { words.push({ text: p, weight: 1 }); }
    });
  });
  words.sort((a, b) => b.weight - a.weight);
  const top = words.slice(0, 18);
  const maxW = Math.max(...top.map(w => w.weight), 1);
  const palettes = [
    { color: '#6366f1', bg: '#eef2ff' }, { color: '#ec4899', bg: '#fdf2f8' },
    { color: '#f97316', bg: '#fff7ed' }, { color: '#10b981', bg: '#ecfdf5' },
    { color: '#ef4444', bg: '#fef2f2' }, { color: '#8b5cf6', bg: '#f5f3ff' },
  ];
  return top.map((w, i) => {
    const ratio = w.weight / maxW;
    const tier = ratio > 0.6 ? 2 : ratio > 0.3 ? 1 : 0;
    const palette = palettes[i % palettes.length];
    return { text: w.text, tier, color: palette.color, bg: palette.bg };
  });
});

// 实时动态
const liveFeeds = ref([
  { time: '刚刚', text: '系统监测到新的热搜话题上榜' },
  { time: '1分钟前', text: '科技分类新增3条热点资讯' },
  { time: '5分钟前', text: '娱乐板块热度持续攀升' },
  { time: '10分钟前', text: '时政热点排名发生变化' },
]);

function addLiveFeed() {
  const actions = [
    '新增热搜话题上榜', '某话题热度飙升50%', '财经板块新增热点', '科技分类热度刷新',
    '体育赛事相关话题上升', '教育领域话题引发讨论', '美食类内容持续火热',
  ];
  const cats = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育'];
  const cat = cats[Math.floor(Math.random() * cats.length)];
  const action = actions[Math.floor(Math.random() * actions.length)];
  liveFeeds.value.unshift({ time: '刚刚', text: `${cat}${action}` });
  if (liveFeeds.value.length > 10) liveFeeds.value = liveFeeds.value.slice(0, 10);
  // 更新时间
  liveFeeds.value.forEach((f, i) => {
    if (i === 0) f.time = '刚刚';
    else if (i === 1) f.time = '1分钟前';
    else if (i < 5) f.time = `${i}分钟前`;
    else f.time = `${i * 2}分钟前`;
  });
}

// 分类统计
const categoryStats = computed(() => {
  const map = {};
  items.value.forEach(i => {
    const cat = i.category || '其他';
    map[cat] = (map[cat] || 0) + 1;
  });
  const result = Object.entries(map).map(([name, count]) => ({
    name, count, color: categoryColors[name] || '#8b5cf6',
    percent: items.value.length ? Math.round((count / items.value.length) * 100) : 0,
  }));
  result.sort((a, b) => b.count - a.count);
  return result;
});

const pieGradient = computed(() => {
  if (!categoryStats.value.length) return '#f1f5f9';
  let start = 0;
  const stops = categoryStats.value.map(cat => {
    const end = start + cat.percent;
    const s = `${cat.color} ${start}% ${end}%`;
    start = end;
    return s;
  });
  return `conic-gradient(${stops.join(', ')})`;
});

// 自动刷新
watch(autoRefresh, (val) => {
  if (val) { countdown.value = 30; startTimer(); }
  else { clearInterval(refreshTimer); }
});

function startTimer() {
  clearInterval(refreshTimer);
  refreshTimer = setInterval(() => {
    countdown.value--;
    if (countdown.value <= 0) {
      countdown.value = 30;
      fetchList();
    }
  }, 1000);
}

onMounted(() => {
  feedTimer = setInterval(addLiveFeed, 15000);
});
onUnmounted(() => {
  clearInterval(refreshTimer);
  clearInterval(feedTimer);
});

// 数据导出
function exportData() {
  const data = filteredItems.value.map(i => ({
    排名: i.rank, 话题: i.title, 热度: i.heat_value, 分类: i.category, 日期: i.collected_at?.slice(0, 10),
  }));
  const csv = ['排名,话题,热度,分类,日期', ...data.map(r => `${r.排名},"${r.话题}",${r.热度},${r.分类},${r.日期}`)].join('\n');
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = `热榜数据_${new Date().toISOString().slice(0, 10)}.csv`;
  a.click(); URL.revokeObjectURL(url);
  ElMessage.success('导出成功');
}

async function fetchList() {
  loading.value = true;
  try {
    const res = await request.get('/hot/list', { params: { page: page.value, category: category.value || undefined, sort_by: sortBy.value, keyword: keyword.value || undefined } });
    items.value = res.items || [];
    total.value = res.total || 0;
    maxHeat = Math.max(...items.value.map(i => i.heat_value || 1), 1);
    items.value.forEach(i => {
      if (!i.heat_trend) i.heat_trend = Math.random() > 0.5 ? 'up' : 'down';
    });
  } finally {
    loading.value = false;
  }
}

function goDetail(row) { router.push(`/hot/${row.id}`); }
function formatHeat(val) { return val > 10000 ? Math.round(val / 10000) + 'w' : val; }
function heatPercent(val) { return Math.round((val / maxHeat) * 100); }
onMounted(fetchList);
</script>

<style scoped>
.hot-page { width: 100%; }

/* Stats */
.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px 24px;
  display: flex; align-items: center; gap: 16px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all .2s;
}
.stat-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.stat-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
}
.stat-value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }

/* Layout */
.hot-layout { display: grid; grid-template-columns: 1fr 320px; gap: 20px; }
.hot-main { min-width: 0; }
.hot-sidebar { display: flex; flex-direction: column; gap: 16px; }

/* Filter */
.filter-card { margin-bottom: 16px; }
.filter-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.filter-right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.filter-tools { display: flex; align-items: center; gap: 16px; margin-top: 12px; padding-top: 12px; border-top: 1px solid #f1f5f9; }

/* Chart */
.chart-card { margin-bottom: 16px; }
.chart-header { display: flex; align-items: center; justify-content: space-between; }
.chart-title { font-size: 16px; font-weight: 600; }
.chart-container { padding: 8px 0; }

.bar-chart { display: flex; flex-direction: column; gap: 12px; }
.bar-item { display: flex; align-items: center; gap: 12px; }
.bar-label { width: 48px; font-size: 13px; font-weight: 500; text-align: right; flex-shrink: 0; }
.bar-track { flex: 1; height: 24px; background: #f1f5f9; border-radius: 12px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 12px; transition: width .6s ease; min-width: 2px; }
.bar-value { width: 40px; font-size: 14px; font-weight: 600; color: var(--text-primary); }

.pie-chart { display: flex; align-items: center; gap: 40px; padding: 16px; }
.pie-visual {
  width: 180px; height: 180px; border-radius: 50%; flex-shrink: 0;
  position: relative; display: flex; align-items: center; justify-content: center;
}
.pie-center {
  width: 80px; height: 80px; background: var(--bg-card); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; color: var(--text-primary);
}
.pie-legend { display: flex; flex-direction: column; gap: 10px; }
.legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.legend-dot { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }
.legend-name { font-weight: 500; min-width: 40px; }
.legend-val { color: var(--text-secondary); }

/* Table */
.table-card { overflow: hidden; }
.rank-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  border-radius: 8px;
  font-size: 13px; font-weight: 700;
  background: #f1f5f9; color: var(--text-secondary);
}
.rank-1 { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #fff; }
.rank-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #fff; }
.rank-3 { background: linear-gradient(135deg, #d97706, #f59e0b); color: #fff; }

.topic-cell { display: flex; align-items: center; gap: 8px; }
.topic-title { font-weight: 500; }
.fav-star { font-size: 12px; }
.risk-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #ef4444;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .4; }
}

.heat-cell { position: relative; padding: 4px 0; display: flex; align-items: center; gap: 4px; }
.heat-bar {
  position: absolute; left: 0; bottom: 0;
  height: 3px; border-radius: 2px;
  background: linear-gradient(90deg, #6366f1, #a78bfa);
  transition: width .3s;
}
.heat-text { font-size: 13px; font-weight: 600; color: var(--primary); position: relative; }
.trend-up { color: #ef4444; font-size: 12px; font-weight: 700; }
.trend-down { color: #10b981; font-size: 12px; font-weight: 700; }
.date-text { font-size: 13px; color: var(--text-secondary); }

.pagination-wrap { display: flex; justify-content: center; padding: 16px 0 4px; }

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

/* Word Cloud — tag-style, 3 tiers */
.word-cloud {
  display: flex; flex-wrap: wrap; gap: 8px;
  padding: 4px 0; min-height: 80px;
}
.cloud-word {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 16px;
  border: 1.5px solid;
  cursor: pointer;
  transition: all .2s;
  white-space: nowrap;
  line-height: 1.4;
}
.tier-0 { font-size: 12px; font-weight: 500; padding: 3px 10px; border-radius: 12px; }
.tier-1 { font-size: 13px; font-weight: 600; padding: 5px 12px; border-radius: 14px; }
.tier-2 { font-size: 14px; font-weight: 700; padding: 6px 14px; border-radius: 16px; }
.cloud-word:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }

/* Rising */
.rising-list { display: flex; flex-direction: column; gap: 2px; }
.rising-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0; border-bottom: 1px solid #f8fafc;
  cursor: pointer; transition: all .15s;
}
.rising-item:hover { padding-left: 4px; }
.rising-item:last-child { border-bottom: none; }
.rising-rank {
  width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; background: #f1f5f9; color: var(--text-secondary); flex-shrink: 0;
}
.rising-1 { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #fff; }
.rising-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #fff; }
.rising-3 { background: linear-gradient(135deg, #d97706, #f59e0b); color: #fff; }
.rising-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.rising-title { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rising-heat { font-size: 12px; color: #f59e0b; }
.rising-arrow { color: #ef4444; font-weight: 700; font-size: 14px; }

/* Live Feed */
.live-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #ef4444; animation: pulse 2s infinite;
}
.live-feed { display: flex; flex-direction: column; gap: 8px; max-height: 240px; overflow-y: auto; }
.feed-item {
  display: flex; gap: 8px; font-size: 13px; line-height: 1.5;
  padding: 6px 0; border-bottom: 1px solid #f8fafc;
}
.feed-item:last-child { border-bottom: none; }
.feed-time { color: var(--text-secondary); flex-shrink: 0; font-size: 12px; min-width: 60px; }
.feed-text { color: var(--text-primary); }

/* Risk */
.risk-list { display: flex; flex-direction: column; gap: 2px; }
.risk-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 0; cursor: pointer; font-size: 13px;
  transition: all .15s;
}
.risk-item:hover { padding-left: 4px; }
.risk-icon { font-size: 12px; }
.risk-title { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.no-risk { text-align: center; color: var(--text-secondary); padding: 12px 0; font-size: 13px; }
</style>