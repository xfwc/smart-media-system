<template>
  <div class="idea-page">
    <div class="page-header">
      <h2>💡 点子库</h2>
      <div class="header-actions">
        <el-input v-model="searchKey" placeholder="搜索点子..." prefix-icon="Search" clearable
          style="width: 220px" @input="fetchList" />
        <el-button type="primary" @click="$router.push('/ideas/create')" round>+ 发布点子</el-button>
      </div>
    </div>

    <!-- 精选推荐横幅 -->
    <div class="featured-banner" v-if="featuredItem">
      <div class="featured-content">
        <el-tag effect="dark" round size="small" type="warning">🌟 精选推荐</el-tag>
        <h3 class="featured-title">{{ featuredItem.title }}</h3>
        <p class="featured-preview">{{ featuredItem.content_preview }}</p>
        <div class="featured-meta">
          <span>👍 {{ featuredItem.likes_count }}</span>
          <span>💬 {{ featuredItem.comments_count }}</span>
          <span>{{ featuredItem.author_name }}</span>
        </div>
        <el-button type="primary" size="small" round @click="$router.push(`/ideas/${featuredItem.id}`)">查看详情</el-button>
      </div>
      <div class="featured-decoration">
        <div class="deco-circle c1"></div>
        <div class="deco-circle c2"></div>
      </div>
    </div>

    <el-card class="filter-card">
      <div class="filters">
        <el-radio-group v-model="category" @change="fetchList" size="default">
          <el-radio-button value="">全部</el-radio-button>
          <el-radio-button v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</el-radio-button>
        </el-radio-group>
        <div style="margin-left: auto; display: flex; gap: 8px;">
          <el-button :type="sortBy === 'hot' ? 'primary' : 'default'" round @click="sortBy = 'hot'; fetchList()">🔥 热门</el-button>
          <el-button :type="sortBy === 'new' ? 'primary' : 'default'" round @click="sortBy = 'new'; fetchList()">🕐 最新</el-button>
          <el-button :type="showFavOnly ? 'warning' : 'default'" round @click="showFavOnly = !showFavOnly">
            ⭐ {{ showFavOnly ? '仅收藏' : '收藏' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 统计概览 -->
    <div class="mini-stats">
      <div class="mini-stat">
        <span class="mini-value">{{ items.length }}</span>
        <span class="mini-label">个点子</span>
      </div>
      <div class="mini-stat">
        <span class="mini-value">{{ totalLikes }}</span>
        <span class="mini-label">总点赞</span>
      </div>
      <div class="mini-stat">
        <span class="mini-value">{{ totalComments }}</span>
        <span class="mini-label">总评论</span>
      </div>
      <div class="mini-stat">
        <span class="mini-value">{{ favorites.length }}</span>
        <span class="mini-label">已收藏</span>
      </div>
    </div>

    <!-- 三栏布局 -->
    <div class="idea-layout">
      <!-- 左侧主区域 -->
      <div class="idea-main">
        <div class="card-grid" v-loading="loading">
          <div v-for="item in displayedItems" :key="item.id" class="idea-card" @click="$router.push(`/ideas/${item.id}`)">
            <div class="card-top">
              <el-tag size="small" effect="plain" round>{{ item.category }}</el-tag>
              <div class="card-stats">
                <span>👍 {{ item.likes_count }}</span>
                <span>💬 {{ item.comments_count }}</span>
              </div>
            </div>
            <h3 class="card-title">{{ item.title }}</h3>
            <p class="card-preview">{{ item.content_preview }}</p>
            <div class="card-tags" v-if="item.tags?.length">
              <el-tag v-for="tag in item.tags.slice(0, 3)" :key="tag" size="small" type="info" effect="plain" round>{{ tag }}</el-tag>
            </div>
            <div class="card-footer">
              <div class="author-info">
                <div class="author-avatar">{{ item.author_name?.charAt(0) }}</div>
                <span class="author-name">{{ item.author_name }}</span>
              </div>
              <el-button :type="isFavorite(item.id) ? 'warning' : 'default'" size="small" circle
                @click.stop="toggleFavorite(item)">
                {{ isFavorite(item.id) ? '⭐' : '☆' }}
              </el-button>
            </div>
          </div>
        </div>
        <el-empty v-if="!displayedItems.length && !loading" description="暂无点子，快来发布第一个吧" />
      </div>

      <!-- 右侧边栏 -->
      <div class="idea-sidebar">
        <!-- 热门标签云 -->
        <div class="sidebar-card">
          <div class="sidebar-title">🏷️ 热门标签</div>
          <div class="tag-cloud">
            <el-tag v-for="tag in popularTags" :key="tag.name" :type="tag.type" effect="plain" round
              :size="tag.size" class="cloud-tag" @click="searchByTag(tag.name)">
              {{ tag.name }} ({{ tag.count }})
            </el-tag>
          </div>
        </div>

        <!-- 点子排行榜 -->
        <div class="sidebar-card">
          <div class="sidebar-title">🏆 点子排行榜</div>
          <el-tabs v-model="rankTab" size="small">
            <el-tab-pane label="🔥 热门" name="hot">
              <div class="rank-list">
                <div v-for="(item, i) in hotRankItems" :key="item.id" class="rank-item" @click="$router.push(`/ideas/${item.id}`)">
                  <span class="rank-num" :class="'rank-' + Math.min(i + 1, 3)">{{ i + 1 }}</span>
                  <div class="rank-info">
                    <span class="rank-title">{{ item.title }}</span>
                    <span class="rank-meta">👍 {{ item.likes_count }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
            <el-tab-pane label="💬 评论" name="comments">
              <div class="rank-list">
                <div v-for="(item, i) in commentRankItems" :key="item.id" class="rank-item" @click="$router.push(`/ideas/${item.id}`)">
                  <span class="rank-num" :class="'rank-' + Math.min(i + 1, 3)">{{ i + 1 }}</span>
                  <div class="rank-info">
                    <span class="rank-title">{{ item.title }}</span>
                    <span class="rank-meta">💬 {{ item.comments_count }}</span>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 活跃创作者 -->
        <div class="sidebar-card">
          <div class="sidebar-title">🎨 活跃创作者</div>
          <div class="creator-list">
            <div v-for="creator in topCreators" :key="creator.name" class="creator-item">
              <div class="creator-avatar" :style="{ background: creator.color }">{{ creator.name.charAt(0) }}</div>
              <div class="creator-info">
                <span class="creator-name">{{ creator.name }}</span>
                <span class="creator-stats">{{ creator.count }}个点子 · 👍 {{ creator.likes }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分类分布 -->
        <div class="sidebar-card">
          <div class="sidebar-title">📊 分类分布</div>
          <div class="dist-list">
            <div v-for="cat in categoryDist" :key="cat.name" class="dist-item">
              <span class="dist-label">{{ cat.name }}</span>
              <div class="dist-track">
                <div class="dist-fill" :style="{ width: cat.percent + '%' }"></div>
              </div>
              <span class="dist-value">{{ cat.count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const items = ref([]);
const loading = ref(true);
const category = ref('');
const sortBy = ref('hot');
const searchKey = ref('');
const showFavOnly = ref(false);
const rankTab = ref('hot');
const categories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];

// 收藏
const favorites = ref(JSON.parse(localStorage.getItem('idea_favorites') || '[]'));
function isFavorite(id) { return favorites.value.includes(id); }
function toggleFavorite(item) {
  const idx = favorites.value.indexOf(item.id);
  if (idx >= 0) { favorites.value.splice(idx, 1); ElMessage.success('已取消收藏'); }
  else { favorites.value.push(item.id); ElMessage.success('已收藏'); }
  localStorage.setItem('idea_favorites', JSON.stringify(favorites.value));
}

// 精选推荐
const featuredItem = computed(() => {
  if (!items.value.length) return null;
  const sorted = [...items.value].sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0));
  return sorted[0];
});

// 搜索过滤
const displayedItems = computed(() => {
  let list = items.value;
  if (showFavOnly.value) list = list.filter(i => favorites.value.includes(i.id));
  if (searchKey.value) {
    const key = searchKey.value.toLowerCase();
    list = list.filter(i => i.title?.toLowerCase().includes(key) || i.content_preview?.toLowerCase().includes(key));
  }
  return list;
});

const totalLikes = computed(() => items.value.reduce((s, i) => s + (i.likes_count || 0), 0));
const totalComments = computed(() => items.value.reduce((s, i) => s + (i.comments_count || 0), 0));

// 热门标签
const popularTags = computed(() => {
  const map = {};
  items.value.forEach(item => {
    (item.tags || []).forEach(tag => { map[tag] = (map[tag] || 0) + 1; });
  });
  const types = ['', 'success', 'warning', 'danger', 'info'];
  const sizes = ['default', 'default', 'small', 'small', 'small'];
  return Object.entries(map)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([name, count], i) => ({
      name, count,
      type: types[i % types.length],
      size: count > 3 ? 'default' : 'small',
    }));
});

// 排行榜
const hotRankItems = computed(() => {
  return [...items.value].sort((a, b) => (b.likes_count || 0) - (a.likes_count || 0)).slice(0, 8);
});
const commentRankItems = computed(() => {
  return [...items.value].sort((a, b) => (b.comments_count || 0) - (a.comments_count || 0)).slice(0, 8);
});

// 活跃创作者
const topCreators = computed(() => {
  const map = {};
  items.value.forEach(item => {
    const name = item.author_name || '匿名';
    if (!map[name]) map[name] = { name, count: 0, likes: 0 };
    map[name].count++;
    map[name].likes += (item.likes_count || 0);
  });
  const colors = ['linear-gradient(135deg, #6366f1, #a78bfa)', 'linear-gradient(135deg, #ec4899, #f472b6)', 'linear-gradient(135deg, #f59e0b, #fbbf24)', 'linear-gradient(135deg, #10b981, #34d399)', 'linear-gradient(135deg, #f97316, #fb923c)'];
  return Object.values(map)
    .sort((a, b) => b.count - a.count)
    .slice(0, 5)
    .map((c, i) => ({ ...c, color: colors[i % colors.length] }));
});

// 分类分布
const categoryDist = computed(() => {
  const map = {};
  items.value.forEach(item => {
    const cat = item.category || '其他';
    map[cat] = (map[cat] || 0) + 1;
  });
  const total = items.value.length || 1;
  return Object.entries(map)
    .map(([name, count]) => ({ name, count, percent: Math.round((count / total) * 100) }))
    .sort((a, b) => b.count - a.count);
});

function searchByTag(tag) {
  searchKey.value = tag;
}

async function fetchList() {
  loading.value = true;
  try {
    const res = await request.get('/ideas', { params: { category: category.value || undefined, sort_by: sortBy.value } });
    items.value = res.items || [];
  } finally { loading.value = false; }
}

onMounted(fetchList);
</script>

<style scoped>
.idea-page { width: 100%; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 22px; font-weight: 700; }
.header-actions { display: flex; gap: 12px; align-items: center; }

/* Featured */
.featured-banner {
  background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 50%, #6366f1 100%);
  border-radius: var(--radius);
  padding: 28px 32px;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
  color: #fff;
}
.featured-content { position: relative; z-index: 1; }
.featured-title { font-size: 20px; font-weight: 700; margin: 10px 0 8px; line-height: 1.4; }
.featured-preview { font-size: 14px; opacity: .8; line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 12px; }
.featured-meta { display: flex; gap: 16px; font-size: 13px; opacity: .7; margin-bottom: 14px; }
.featured-decoration { position: absolute; right: -20px; top: -20px; }
.deco-circle { position: absolute; border-radius: 50%; background: rgba(255,255,255,.08); }
.c1 { width: 200px; height: 200px; right: -40px; top: -60px; }
.c2 { width: 120px; height: 120px; right: 60px; top: 20px; }

.filter-card { margin-bottom: 16px; }
.filters { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }

/* Mini stats */
.mini-stats {
  display: flex; gap: 24px; margin-bottom: 16px;
  padding: 12px 20px; background: var(--bg-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}
.mini-stat { display: flex; align-items: baseline; gap: 4px; }
.mini-value { font-size: 18px; font-weight: 700; color: var(--primary); }
.mini-label { font-size: 13px; color: var(--text-secondary); }

/* Layout */
.idea-layout { display: grid; grid-template-columns: 1fr 320px; gap: 20px; }
.idea-main { min-width: 0; }
.idea-sidebar { display: flex; flex-direction: column; gap: 16px; }

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.idea-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: all .25s;
  display: flex; flex-direction: column;
}
.idea-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
  border-color: var(--primary);
}

.card-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.card-stats { display: flex; gap: 12px; font-size: 13px; color: var(--text-secondary); }

.card-title {
  font-size: 16px; font-weight: 600;
  margin-bottom: 8px; line-height: 1.5;
  display: -webkit-box; -webkit-line-clamp: 2;
  -webkit-box-orient: vertical; overflow: hidden;
}
.card-preview {
  font-size: 14px; line-height: 1.6; color: var(--text-secondary);
  display: -webkit-box; -webkit-line-clamp: 3;
  -webkit-box-orient: vertical; overflow: hidden;
  flex: 1;
}
.card-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }

.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 16px; padding-top: 12px; border-top: 1px solid #f1f5f9; }
.author-info { display: flex; align-items: center; gap: 8px; }
.author-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; color: #fff;
}
.author-name { font-size: 13px; color: var(--text-secondary); }

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

/* Tag Cloud */
.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; }
.cloud-tag { cursor: pointer; transition: all .2s; }
.cloud-tag:hover { transform: scale(1.05); }

/* Rank */
.rank-list { display: flex; flex-direction: column; gap: 2px; }
.rank-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0; border-bottom: 1px solid #f8fafc;
  cursor: pointer; transition: all .15s;
}
.rank-item:hover { padding-left: 4px; }
.rank-item:last-child { border-bottom: none; }
.rank-num {
  width: 24px; height: 24px; border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; background: #f1f5f9; color: var(--text-secondary); flex-shrink: 0;
}
.rank-1 { background: linear-gradient(135deg, #f59e0b, #fbbf24); color: #fff; }
.rank-2 { background: linear-gradient(135deg, #94a3b8, #cbd5e1); color: #fff; }
.rank-3 { background: linear-gradient(135deg, #d97706, #f59e0b); color: #fff; }
.rank-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.rank-title { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.rank-meta { font-size: 12px; color: var(--text-secondary); }

/* Creator */
.creator-list { display: flex; flex-direction: column; gap: 10px; }
.creator-item { display: flex; align-items: center; gap: 10px; }
.creator-avatar {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.creator-info { display: flex; flex-direction: column; gap: 2px; }
.creator-name { font-size: 14px; font-weight: 600; }
.creator-stats { font-size: 12px; color: var(--text-secondary); }

/* Distribution */
.dist-list { display: flex; flex-direction: column; gap: 8px; }
.dist-item { display: flex; align-items: center; gap: 10px; }
.dist-label { width: 48px; font-size: 13px; font-weight: 500; text-align: right; flex-shrink: 0; }
.dist-track { flex: 1; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
.dist-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #a78bfa); border-radius: 4px; transition: width .5s; }
.dist-value { width: 30px; font-size: 14px; font-weight: 600; color: var(--primary); }
</style>