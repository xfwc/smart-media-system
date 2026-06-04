<template>
  <div class="admin-page" v-loading="loading">
    <!-- 数据统计 -->
    <div class="stats-row">
      <div v-for="s in statsCards" :key="s.label" class="stat-card">
        <div class="stat-icon" :style="{ background: s.gradient }">{{ s.icon }}</div>
        <div class="stat-body">
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <!-- 标签页 -->
    <el-card class="main-card">
      <el-tabs v-model="activeTab">
        <!-- 待审核点子 -->
        <el-tab-pane label="待审核点子" name="review">
          <div class="tab-toolbar">
            <el-input v-model="reviewSearch" placeholder="搜索点子..." prefix-icon="Search" clearable style="width: 250px" />
            <el-button type="success" size="small" round @click="batchReview('approve')" :disabled="!selectedIdeas.length">
              ✅ 批量通过 ({{ selectedIdeas.length }})
            </el-button>
            <el-button type="danger" size="small" round @click="batchReview('reject')" :disabled="!selectedIdeas.length">
              ❌ 批量拒绝 ({{ selectedIdeas.length }})
            </el-button>
          </div>
          <el-table :data="filteredPendingIdeas" stripe style="width: 100%" @selection-change="onSelectionChange">
            <el-table-column type="selection" width="50" />
            <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="author" label="作者" width="120" />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" round>{{ row.category }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="提交时间" width="160">
              <template #default="{ row }">
                <span class="date-text">{{ row.created_at?.slice(0, 16) || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button type="primary" size="small" text @click="previewIdea(row)">预览</el-button>
                <el-button type="success" size="small" round @click="review(row.id, 'approve')">通过</el-button>
                <el-popconfirm title="确定拒绝该点子？" @confirm="review(row.id, 'reject')">
                  <template #reference>
                    <el-button type="danger" size="small" round>拒绝</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!filteredPendingIdeas.length" description="暂无待审核点子" :image-size="60" />
        </el-tab-pane>

        <!-- 用户管理 -->
        <el-tab-pane label="用户管理" name="users">
          <div class="tab-toolbar">
            <el-input v-model="userSearch" placeholder="搜索用户..." prefix-icon="Search" clearable style="width: 250px" />
          </div>
          <el-table :data="filteredUsers" stripe style="width: 100%">
            <el-table-column prop="username" label="用户名" min-width="150" />
            <el-table-column prop="email" label="邮箱" min-width="200">
              <template #default="{ row }">
                <span>{{ row.email || '未绑定' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="role" label="角色" width="120">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' || row.role === 'superadmin' ? 'danger' : 'primary'" size="small" effect="dark" round>
                  {{ row.role === 'admin' || row.role === 'superadmin' ? '管理员' : '创作者' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_active" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.is_active !== false ? 'success' : 'danger'" size="small" effect="plain" round>
                  {{ row.is_active !== false ? '正常' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="160">
              <template #default="{ row }">
                <span class="date-text">{{ row.created_at?.slice(0, 10) || '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button v-if="row.role !== 'superadmin'" size="small" text type="primary"
                  @click="toggleUserRole(row)">
                  {{ row.role === 'admin' ? '降为创作者' : '升为管理员' }}
                </el-button>
                <el-button v-if="row.role !== 'superadmin'" size="small" text
                  :type="row.is_active !== false ? 'danger' : 'success'"
                  @click="toggleUserActive(row)">
                  {{ row.is_active !== false ? '禁用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!filteredUsers.length" description="暂无用户数据" :image-size="60" />
        </el-tab-pane>

        <!-- 热点管理 -->
        <el-tab-pane label="热点管理" name="topics">
          <div class="tab-toolbar">
            <el-input v-model="topicSearch" placeholder="搜索热点..." prefix-icon="Search" clearable style="width: 250px" />
            <el-button type="primary" size="small" round @click="fetchTopics">🔄 刷新热点</el-button>
          </div>
          <el-table :data="filteredTopics" stripe style="width: 100%">
            <el-table-column prop="rank" label="排名" width="80" align="center" />
            <el-table-column prop="title" label="话题" min-width="300" show-overflow-tooltip />
            <el-table-column prop="heat_value" label="热度" width="120" sortable />
            <el-table-column prop="category" label="分类" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" round>{{ row.category || '其他' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="risk_level" label="风险" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.risk_level" :type="row.risk_level === 'high' ? 'danger' : row.risk_level === 'medium' ? 'warning' : 'success'" size="small" effect="dark" round>
                  {{ row.risk_level === 'high' ? '高' : row.risk_level === 'medium' ? '中' : '低' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!filteredTopics.length" description="暂无热点数据" :image-size="60" />
        </el-tab-pane>

        <!-- 数据概览 -->
        <el-tab-pane label="数据概览" name="stats">
          <div class="overview-grid">
            <div v-for="s in statsCards" :key="s.label + '-ov'" class="overview-item">
              <div class="overview-icon" :style="{ background: s.gradient }">{{ s.icon }}</div>
              <span class="overview-label">{{ s.label }}</span>
              <span class="overview-value">{{ s.value }}</span>
            </div>
          </div>
          <!-- 分类分布 -->
          <div class="category-dist" v-if="topicCategories.length">
            <h4 class="dist-title">📊 热点分类分布</h4>
            <div class="dist-bars">
              <div v-for="cat in topicCategories" :key="cat.name" class="dist-bar-item">
                <span class="dist-label">{{ cat.name }}</span>
                <div class="dist-track">
                  <div class="dist-fill" :style="{ width: cat.percent + '%' }"></div>
                </div>
                <span class="dist-value">{{ cat.count }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 系统日志 -->
        <el-tab-pane label="系统日志" name="logs">
          <div class="tab-toolbar">
            <el-radio-group v-model="logLevel" size="small">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="info">INFO</el-radio-button>
              <el-radio-button value="warning">WARNING</el-radio-button>
              <el-radio-button value="error">ERROR</el-radio-button>
            </el-radio-group>
            <el-button size="small" text @click="clearLogs">清空日志</el-button>
          </div>
          <div class="log-list">
            <div v-for="(log, i) in filteredLogs" :key="i" class="log-item" :class="'log-' + log.level">
              <span class="log-level">{{ log.level.toUpperCase() }}</span>
              <span class="log-time">{{ log.time }}</span>
              <span class="log-msg">{{ log.message }}</span>
            </div>
            <div v-if="!filteredLogs.length" class="no-logs">暂无日志记录</div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewVisible" title="点子预览" width="600px">
      <div v-if="previewData" class="preview-content">
        <h3>{{ previewData.title }}</h3>
        <div class="preview-meta">
          <el-tag size="small" effect="plain" round>{{ previewData.category }}</el-tag>
          <span>作者：{{ previewData.author }}</span>
        </div>
        <p class="preview-text">{{ previewData.content || '暂无内容' }}</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const loading = ref(true);
const pendingIdeas = ref([]);
const users = ref([]);
const topics = ref([]);
const stats = ref({});
const activeTab = ref('review');
const reviewSearch = ref('');
const userSearch = ref('');
const topicSearch = ref('');
const logLevel = ref('');
const selectedIdeas = ref([]);
const previewVisible = ref(false);
const previewData = ref(null);

const statsCards = ref([
  { label: '用户总数', value: 0, icon: '👥', gradient: 'linear-gradient(135deg, #6366f1, #818cf8)' },
  { label: '热点总数', value: 0, icon: '🔥', gradient: 'linear-gradient(135deg, #f97316, #fb923c)' },
  { label: '推荐总数', value: 0, icon: '📋', gradient: 'linear-gradient(135deg, #10b981, #34d399)' },
  { label: '企划总数', value: 0, icon: '📝', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)' },
  { label: '点子总数', value: 0, icon: '💡', gradient: 'linear-gradient(135deg, #ec4899, #f472b6)' },
]);

// 过滤
const filteredPendingIdeas = computed(() => {
  if (!reviewSearch.value) return pendingIdeas.value;
  const key = reviewSearch.value.toLowerCase();
  return pendingIdeas.value.filter(i => i.title?.toLowerCase().includes(key) || i.author?.toLowerCase().includes(key));
});
const filteredUsers = computed(() => {
  if (!userSearch.value) return users.value;
  const key = userSearch.value.toLowerCase();
  return users.value.filter(u => u.username?.toLowerCase().includes(key) || u.email?.toLowerCase().includes(key));
});
const filteredTopics = computed(() => {
  if (!topicSearch.value) return topics.value;
  const key = topicSearch.value.toLowerCase();
  return topics.value.filter(t => t.title?.toLowerCase().includes(key));
});

// 分类统计
const topicCategories = computed(() => {
  const map = {};
  topics.value.forEach(t => { const cat = t.category || '其他'; map[cat] = (map[cat] || 0) + 1; });
  const total = topics.value.length || 1;
  return Object.entries(map).map(([name, count]) => ({ name, count, percent: Math.round(count / total * 100) }))
    .sort((a, b) => b.count - a.count);
});

// 系统日志（模拟）
const systemLogs = ref([
  { level: 'info', time: new Date().toLocaleString('zh-CN'), message: '系统启动完成' },
  { level: 'info', time: new Date().toLocaleString('zh-CN'), message: '数据库连接成功' },
  { level: 'info', time: new Date().toLocaleString('zh-CN'), message: 'API 服务已启动于端口 8000' },
  { level: 'warning', time: new Date().toLocaleString('zh-CN'), message: 'Redis 服务未连接，缓存功能不可用' },
  { level: 'info', time: new Date().toLocaleString('zh-CN'), message: '用户 admin 登录成功' },
]);
const filteredLogs = computed(() => {
  if (!logLevel.value) return systemLogs.value;
  return systemLogs.value.filter(l => l.level === logLevel.value);
});
function clearLogs() { systemLogs.value = []; ElMessage.success('日志已清空'); }

function onSelectionChange(val) { selectedIdeas.value = val; }
async function batchReview(action) {
  for (const idea of selectedIdeas.value) {
    await request.post(`/admin/ideas/${idea.id}/review?action=${action}`).catch(() => {});
  }
  ElMessage.success(`已批量${action === 'approve' ? '通过' : '拒绝'} ${selectedIdeas.value.length} 个点子`);
  load();
}

function previewIdea(row) {
  previewData.value = row;
  previewVisible.value = true;
}

async function toggleUserRole(row) {
  const newRole = row.role === 'admin' ? 'creator' : 'admin';
  try {
    await request.put(`/admin/users/${row.id}/role`, { role: newRole });
    ElMessage.success('角色已更新');
    load();
  } catch {}
}

async function toggleUserActive(row) {
  const newActive = row.is_active === false ? true : false;
  try {
    await request.put(`/admin/users/${row.id}/active`, { is_active: newActive });
    ElMessage.success(newActive ? '用户已启用' : '用户已禁用');
    load();
  } catch {}
}

async function fetchTopics() {
  try {
    const res = await request.get('/hot/list', { params: { page_size: 100 } });
    topics.value = res.items || [];
  } catch {}
}

async function load() {
  loading.value = true;
  try {
    const [ideasRes, statsRes, usersRes] = await Promise.allSettled([
      request.get('/admin/ideas/pending'),
      request.get('/admin/stats'),
      request.get('/admin/users').catch(() => ({ items: [] })),
    ]);
    if (ideasRes.status === 'fulfilled') pendingIdeas.value = ideasRes.value.items || [];
    if (statsRes.status === 'fulfilled') {
      stats.value = statsRes.value || {};
      statsCards.value[0].value = stats.value.users_total || 0;
      statsCards.value[1].value = stats.value.topics_total || 0;
      statsCards.value[2].value = stats.value.recommendations_total || 0;
      statsCards.value[3].value = stats.value.plans_total || 0;
      statsCards.value[4].value = stats.value.ideas_total || 0;
    }
    if (usersRes.status === 'fulfilled') users.value = usersRes.value.items || usersRes.value || [];
    fetchTopics();
  } finally { loading.value = false; }
}

async function review(ideaId, action) {
  await request.post(`/admin/ideas/${ideaId}/review?action=${action}`);
  load();
}

onMounted(load);
</script>

<style scoped>
.admin-page { width: 100%; }

.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  display: flex; align-items: center; gap: 14px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all .2s;
}
.stat-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.stat-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px;
}
.stat-value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }

.main-card {}

.tab-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.date-text { font-size: 13px; color: var(--text-secondary); }

/* Overview */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  padding: 8px 0;
}
.overview-item {
  display: flex; flex-direction: column; gap: 8px;
  padding: 20px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
}
.overview-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
}
.overview-label { font-size: 13px; color: var(--text-secondary); }
.overview-value { font-size: 28px; font-weight: 700; color: var(--primary); }

/* Category distribution */
.category-dist { margin-top: 24px; }
.dist-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.dist-bars { display: flex; flex-direction: column; gap: 10px; }
.dist-bar-item { display: flex; align-items: center; gap: 12px; }
.dist-label { width: 60px; font-size: 13px; font-weight: 500; text-align: right; flex-shrink: 0; }
.dist-track { flex: 1; height: 20px; background: #f1f5f9; border-radius: 10px; overflow: hidden; }
.dist-fill { height: 100%; background: linear-gradient(90deg, #6366f1, #a78bfa); border-radius: 10px; transition: width .5s; min-width: 2px; }
.dist-value { width: 36px; font-size: 14px; font-weight: 600; color: var(--primary); }

/* Logs */
.log-list { display: flex; flex-direction: column; gap: 2px; max-height: 500px; overflow-y: auto; }
.log-item {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 14px; border-radius: var(--radius-sm);
  font-size: 13px; font-family: 'Consolas', 'Monaco', monospace;
  background: #f8fafc;
}
.log-item.log-info { border-left: 3px solid #3b82f6; }
.log-item.log-warning { border-left: 3px solid #f59e0b; background: #fffbeb; }
.log-item.log-error { border-left: 3px solid #ef4444; background: #fef2f2; }
.log-level {
  padding: 2px 8px; border-radius: 4px;
  font-size: 11px; font-weight: 700;
  flex-shrink: 0;
}
.log-info .log-level { background: #dbeafe; color: #1d4ed8; }
.log-warning .log-level { background: #fef3c7; color: #92400e; }
.log-error .log-level { background: #fee2e2; color: #991b1b; }
.log-time { color: var(--text-secondary); flex-shrink: 0; font-size: 12px; }
.log-msg { color: var(--text-primary); }
.no-logs { text-align: center; padding: 40px 0; color: var(--text-secondary); }

/* Preview */
.preview-content h3 { font-size: 18px; font-weight: 600; margin-bottom: 12px; }
.preview-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; font-size: 14px; color: var(--text-secondary); }
.preview-text { font-size: 15px; line-height: 1.8; white-space: pre-wrap; }
</style>
