<template>
  <div class="profile-page" v-loading="loading">
    <!-- 个人信息头部 -->
    <div class="profile-header">
      <div class="profile-banner"></div>
      <div class="profile-info">
        <div class="avatar-section">
          <div class="avatar-large">{{ profile?.username?.charAt(0)?.toUpperCase() }}</div>
          <div class="user-meta">
            <h1 class="username">{{ profile?.username }}</h1>
            <div class="user-badges">
              <el-tag :type="profile?.role === 'admin' || profile?.role === 'superadmin' ? 'danger' : 'primary'" effect="dark" size="small" round>
                {{ profile?.role === 'admin' || profile?.role === 'superadmin' ? '管理员' : '创作者' }}
              </el-tag>
              <span class="join-date">加入于 {{ profile?.created_at?.slice(0, 10) || '—' }}</span>
            </div>
          </div>
        </div>
        <el-button type="primary" round @click="pwdDialog = true">修改密码</el-button>
      </div>
    </div>

    <!-- 数据统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #6366f1, #818cf8);">💡</div>
        <div class="stat-body">
          <div class="stat-value">{{ myIdeas.length }}</div>
          <div class="stat-label">发布点子</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #34d399);">❤️</div>
        <div class="stat-body">
          <div class="stat-value">{{ totalLikes }}</div>
          <div class="stat-label">获赞总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #fbbf24);">💬</div>
        <div class="stat-body">
          <div class="stat-value">{{ totalComments }}</div>
          <div class="stat-label">收到评论</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #ec4899, #f472b6);">🎯</div>
        <div class="stat-body">
          <div class="stat-value">{{ selectedInterests.length }}</div>
          <div class="stat-label">关注领域</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #8b5cf6, #a78bfa);">🔥</div>
        <div class="stat-body">
          <div class="stat-value">{{ achievementCount }}</div>
          <div class="stat-label">达成成就</div>
        </div>
      </div>
    </div>

    <!-- 三栏布局 -->
    <div class="profile-grid">
      <!-- 左栏 -->
      <div class="left-col">
        <!-- 关注领域偏好 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title">
              <span>🎯</span> 关注领域偏好
              <el-button v-if="!editing" size="small" text type="primary" @click="editing = true">修改</el-button>
            </div>
          </template>
          <template v-if="!editing">
            <div class="interest-tags" v-if="selectedInterests.length">
              <div v-for="cat in selectedInterests" :key="cat" class="interest-tag">
                <span class="interest-icon">{{ categoryIcon(cat) }}</span>
                {{ cat }}
              </div>
            </div>
            <div v-else class="empty-hint">
              <p>尚未设置偏好领域</p>
              <el-button type="primary" size="small" text @click="editing = true">立即设置</el-button>
            </div>
          </template>
          <template v-else>
            <div class="interest-editor">
              <el-checkbox-group v-model="editInterests">
                <el-checkbox v-for="cat in allCategories" :key="cat" :label="cat">
                  <span>{{ categoryIcon(cat) }} {{ cat }}</span>
                </el-checkbox>
              </el-checkbox-group>
            </div>
            <div class="editor-actions">
              <el-button type="primary" size="small" round @click="saveInterests">保存偏好</el-button>
              <el-button size="small" round @click="editing = false; editInterests = [...selectedInterests]">取消</el-button>
            </div>
          </template>
        </el-card>

        <!-- 创作成就 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>🏆</span> 创作成就</div>
          </template>
          <div class="achievement-grid">
            <div v-for="ach in achievements" :key="ach.id" class="achievement-item" :class="{ unlocked: ach.unlocked }">
              <div class="ach-icon" :style="{ background: ach.unlocked ? ach.gradient : '#e2e8f0' }">{{ ach.icon }}</div>
              <div class="ach-info">
                <span class="ach-name">{{ ach.name }}</span>
                <span class="ach-desc">{{ ach.desc }}</span>
              </div>
              <el-tag v-if="ach.unlocked" type="success" size="small" effect="dark" round>已达成</el-tag>
              <el-tag v-else type="info" size="small" effect="plain" round>{{ ach.progress }}%</el-tag>
            </div>
          </div>
        </el-card>

        <!-- 账号安全 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>🔒</span> 账号安全</div>
          </template>
          <div class="security-list">
            <div class="security-item">
              <div class="security-info">
                <span class="security-label">登录密码</span>
                <span class="security-desc">定期更换密码可提高账号安全性</span>
              </div>
              <el-button size="small" text type="primary" @click="pwdDialog = true">修改</el-button>
            </div>
            <div class="security-item">
              <div class="security-info">
                <span class="security-label">邮箱绑定</span>
                <span class="security-desc">{{ profile?.email || '未绑定' }}</span>
              </div>
              <el-tag :type="profile?.email ? 'success' : 'info'" size="small" effect="plain" round>
                {{ profile?.email ? '已绑定' : '未绑定' }}
              </el-tag>
            </div>
            <div class="security-item">
              <div class="security-info">
                <span class="security-label">账号角色</span>
                <span class="security-desc">当前拥有的权限等级</span>
              </div>
              <el-tag :type="profile?.role === 'admin' || profile?.role === 'superadmin' ? 'danger' : 'primary'" size="small" effect="dark" round>
                {{ profile?.role === 'admin' || profile?.role === 'superadmin' ? '管理员' : '创作者' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 创作活跃度 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>📊</span> 创作活跃度</div>
          </template>
          <div class="activity-chart">
            <div v-for="(day, i) in activityDays" :key="i" class="activity-cell"
              :class="'level-' + day.level" :title="day.date + ': ' + day.count + '篇'">
            </div>
          </div>
          <div class="chart-legend">
            <span>少</span>
            <div class="legend-cell level-0"></div>
            <div class="legend-cell level-1"></div>
            <div class="legend-cell level-2"></div>
            <div class="legend-cell level-3"></div>
            <span>多</span>
          </div>
        </el-card>
      </div>

      <!-- 中栏 -->
      <div class="mid-col">
        <!-- 我的点子 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title">
              <span>💡</span> 我的点子
              <el-button size="small" text type="primary" @click="$router.push('/ideas/create')">发布新点子</el-button>
            </div>
          </template>
          <div v-if="myIdeas.length" class="ideas-list">
            <div v-for="item in myIdeas" :key="item.id" class="idea-card" @click="$router.push(`/ideas/${item.id}`)">
              <div class="idea-left">
                <h4 class="idea-title">{{ item.title }}</h4>
                <div class="idea-meta">
                  <el-tag size="small" effect="plain" round>{{ item.category }}</el-tag>
                  <span class="meta-item">👍 {{ item.likes_count }}</span>
                  <span class="meta-item">💬 {{ item.comments_count }}</span>
                  <span class="meta-date">{{ item.created_at?.slice(0, 10) }}</span>
                </div>
              </div>
              <el-tag :type="statusType(item.status)" size="small" effect="dark" round>
                {{ statusLabel(item.status) }}
              </el-tag>
            </div>
          </div>
          <div v-else class="empty-hint">
            <p>还没有发布过点子</p>
            <el-button type="primary" size="small" round @click="$router.push('/ideas/create')">去发布</el-button>
          </div>
        </el-card>

        <!-- 最近浏览 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title">
              <span>👁️</span> 最近浏览
              <el-button size="small" text @click="clearBrowsing">清空</el-button>
            </div>
          </template>
          <div v-if="browsingHistory.length" class="browsing-list">
            <div v-for="item in browsingHistory" :key="item.id" class="browsing-item" @click="goBrowsing(item)">
              <div class="browsing-icon">{{ item.type === 'hot' ? '🔥' : '💡' }}</div>
              <div class="browsing-info">
                <span class="browsing-title">{{ item.title }}</span>
                <span class="browsing-meta">{{ item.type === 'hot' ? '热点' : '点子' }} · {{ item.time }}</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">
            <p>暂无浏览记录</p>
          </div>
        </el-card>

        <!-- 创作数据概览 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>📈</span> 创作数据概览</div>
          </template>
          <div class="data-overview">
            <div class="data-row">
              <span class="data-label">总发布数</span>
              <span class="data-value">{{ myIdeas.length }}</span>
            </div>
            <div class="data-row">
              <span class="data-label">已通过</span>
              <span class="data-value">{{ myIdeas.filter(i => i.status === 'approved').length }}</span>
            </div>
            <div class="data-row">
              <span class="data-label">审核中</span>
              <span class="data-value">{{ myIdeas.filter(i => i.status === 'pending').length }}</span>
            </div>
            <div class="data-row">
              <span class="data-label">平均获赞</span>
              <span class="data-value">{{ myIdeas.length ? Math.round(totalLikes / myIdeas.length) : 0 }}</span>
            </div>
            <div class="data-row">
              <span class="data-label">通过率</span>
              <span class="data-value">{{ approvalRate }}%</span>
            </div>
            <div class="data-row">
              <span class="data-label">活跃天数</span>
              <span class="data-value">{{ activeDays }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 右栏 -->
      <div class="right-col">
        <!-- 快捷操作 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>⚡</span> 快捷操作</div>
          </template>
          <div class="quick-actions">
            <div class="action-item" @click="$router.push('/hot')">
              <div class="action-icon" style="background: linear-gradient(135deg, #f97316, #fb923c);">🔥</div>
              <span>浏览热榜</span>
            </div>
            <div class="action-item" @click="$router.push('/plan')">
              <div class="action-icon" style="background: linear-gradient(135deg, #6366f1, #818cf8);">📝</div>
              <span>生成企划</span>
            </div>
            <div class="action-item" @click="$router.push('/recommend')">
              <div class="action-icon" style="background: linear-gradient(135deg, #10b981, #34d399);">📋</div>
              <span>选题推荐</span>
            </div>
            <div class="action-item" @click="$router.push('/ideas')">
              <div class="action-icon" style="background: linear-gradient(135deg, #ec4899, #f472b6);">💡</div>
              <span>点子库</span>
            </div>
          </div>
        </el-card>

        <!-- 创作等级 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>⭐</span> 创作等级</div>
          </template>
          <div class="level-section">
            <div class="level-header">
              <span class="level-name">{{ currentLevel.name }}</span>
              <span class="level-range">Lv.{{ currentLevel.min }}-{{ currentLevel.max }}</span>
            </div>
            <div class="level-progress">
              <el-progress :percentage="levelProgress" :stroke-width="10" :show-text="false"
                :color="currentLevel.color" />
              <span class="level-exp">{{ myIdeas.length }} / {{ currentLevel.max }} EXP</span>
            </div>
            <div class="level-perks">
              <div v-for="perk in currentLevel.perks" :key="perk" class="perk-item">✅ {{ perk }}</div>
            </div>
          </div>
        </el-card>

        <!-- 创作偏好分析 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>🧠</span> 偏好分析</div>
          </template>
          <div class="pref-analysis">
            <div v-for="cat in categoryAnalysis" :key="cat.name" class="pref-item">
              <div class="pref-header">
                <span class="pref-name">{{ categoryIcon(cat.name) }} {{ cat.name }}</span>
                <span class="pref-count">{{ cat.count }}篇</span>
              </div>
              <div class="pref-track">
                <div class="pref-fill" :style="{ width: cat.percent + '%', background: cat.color }"></div>
              </div>
            </div>
            <div v-if="!categoryAnalysis.length" class="empty-hint">
              <p>发布点子后将展示偏好分析</p>
            </div>
          </div>
        </el-card>

        <!-- 近期动态 -->
        <el-card class="section-card">
          <template #header>
            <div class="section-title"><span>🔔</span> 近期动态</div>
          </template>
          <div class="timeline-list">
            <div v-for="(event, i) in recentEvents" :key="i" class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <span class="timeline-text">{{ event.text }}</span>
                <span class="timeline-time">{{ event.time }}</span>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="pwdDialog" title="修改密码" width="420px" :close-on-click-modal="false">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-position="top">
        <el-form-item label="原密码" prop="oldPwd">
          <el-input v-model="pwdForm.oldPwd" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPwd">
          <el-input v-model="pwdForm.newPwd" type="password" show-password placeholder="至少8位" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPwd">
          <el-input v-model="pwdForm.confirmPwd" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog = false" round>取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="changePassword" round>确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const router = useRouter();
const profile = ref(null);
const loading = ref(true);
const selectedInterests = ref([]);
const editing = ref(false);
const editInterests = ref([]);
const myIdeas = ref([]);
const allCategories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];

const pwdFormRef = ref(null);
const pwdDialog = ref(false);
const pwdLoading = ref(false);
const pwdForm = reactive({ oldPwd: '', newPwd: '', confirmPwd: '' });
const validateConfirm = (_rule, value, callback) => {
  if (value !== pwdForm.newPwd) callback(new Error('两次密码不一致'));
  else callback();
};
const validateNewPwd = (_rule, value, callback) => {
  if (!value) callback(new Error('新密码不能为空'));
  else if (value.length < 8) callback(new Error('密码至少8位'));
  else if (value === pwdForm.oldPwd) callback(new Error('新密码不能和原密码一样'));
  else callback();
};
const pwdRules = {
  oldPwd: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPwd: [{ required: true, validator: validateNewPwd, trigger: 'blur' }],
  confirmPwd: [{ required: true, validator: validateConfirm, trigger: 'blur' }],
};

const totalLikes = computed(() => myIdeas.value.reduce((sum, i) => sum + (i.likes_count || 0), 0));
const totalComments = computed(() => myIdeas.value.reduce((sum, i) => sum + (i.comments_count || 0), 0));
const approvalRate = computed(() => {
  if (!myIdeas.value.length) return 0;
  const approved = myIdeas.value.filter(i => i.status === 'approved').length;
  return Math.round((approved / myIdeas.value.length) * 100);
});
const activeDays = computed(() => {
  const dates = new Set(myIdeas.value.map(i => i.created_at?.slice(0, 10)).filter(Boolean));
  return dates.size;
});

// 浏览记录
const browsingHistory = ref(JSON.parse(localStorage.getItem('browsing_history') || '[]'));
function clearBrowsing() {
  browsingHistory.value = [];
  localStorage.removeItem('browsing_history');
  ElMessage.success('浏览记录已清空');
}
function goBrowsing(item) {
  if (item.type === 'hot') router.push(`/hot/${item.id}`);
  else router.push(`/ideas/${item.id}`);
}

// 创作等级
const levels = [
  { name: '新手创作者', min: 0, max: 5, color: '#94a3b8', perks: ['发布点子', '浏览热榜'] },
  { name: '初级创作者', min: 5, max: 15, color: '#10b981', perks: ['发布点子', '浏览热榜', '生成企划', '选题推荐'] },
  { name: '中级创作者', min: 15, max: 30, color: '#6366f1', perks: ['全部基础功能', '优先审核', '专属标签'] },
  { name: '高级创作者', min: 30, max: 50, color: '#f59e0b', perks: ['全部中级功能', '数据分析', '优先推荐'] },
  { name: '金牌创作者', min: 50, max: 100, color: '#ef4444', perks: ['全部高级功能', '官方推荐', '专属徽章'] },
];
const currentLevel = computed(() => {
  const count = myIdeas.value.length;
  for (let i = levels.length - 1; i >= 0; i--) {
    if (count >= levels[i].min) return levels[i];
  }
  return levels[0];
});
const levelProgress = computed(() => {
  const count = myIdeas.value.length;
  const level = currentLevel.value;
  if (count >= level.max) return 100;
  return Math.round(((count - level.min) / (level.max - level.min)) * 100);
});

// 创作成就
const achievements = computed(() => {
  const count = myIdeas.value.length;
  const likes = totalLikes.value;
  return [
    { id: 1, name: '初出茅庐', desc: '发布第一个点子', icon: '🌟', gradient: 'linear-gradient(135deg, #6366f1, #a78bfa)', unlocked: count >= 1, progress: Math.min(count, 1) * 100 },
    { id: 2, name: '笔耕不辍', desc: '发布5个点子', icon: '✍️', gradient: 'linear-gradient(135deg, #10b981, #34d399)', unlocked: count >= 5, progress: Math.min(Math.round((count / 5) * 100), 100) },
    { id: 3, name: '内容达人', desc: '发布10个点子', icon: '🏅', gradient: 'linear-gradient(135deg, #f59e0b, #fbbf24)', unlocked: count >= 10, progress: Math.min(Math.round((count / 10) * 100), 100) },
    { id: 4, name: '人气之选', desc: '累计获得50个赞', icon: '💖', gradient: 'linear-gradient(135deg, #ec4899, #f472b6)', unlocked: likes >= 50, progress: Math.min(Math.round((likes / 50) * 100), 100) },
    { id: 5, name: '超级创作者', desc: '发布20个点子', icon: '👑', gradient: 'linear-gradient(135deg, #8b5cf6, #a78bfa)', unlocked: count >= 20, progress: Math.min(Math.round((count / 20) * 100), 100) },
    { id: 6, name: '万人迷', desc: '累计获得200个赞', icon: '🎉', gradient: 'linear-gradient(135deg, #f97316, #fb923c)', unlocked: likes >= 200, progress: Math.min(Math.round((likes / 200) * 100), 100) },
  ];
});
const achievementCount = computed(() => achievements.value.filter(a => a.unlocked).length);

// 偏好分析
const categoryColors = { '时政': '#ef4444', '财经': '#f59e0b', '科技': '#6366f1', '娱乐': '#ec4899', '体育': '#10b981', '美食': '#f97316', '教育': '#3b82f6', '其他': '#8b5cf6' };
const categoryAnalysis = computed(() => {
  const map = {};
  myIdeas.value.forEach(i => { const cat = i.category || '其他'; map[cat] = (map[cat] || 0) + 1; });
  const total = myIdeas.value.length || 1;
  return Object.entries(map)
    .map(([name, count]) => ({ name, count, percent: Math.round((count / total) * 100), color: categoryColors[name] || '#8b5cf6' }))
    .sort((a, b) => b.count - a.count);
});

// 近期动态
const recentEvents = computed(() => {
  const events = [];
  myIdeas.value.slice(0, 5).forEach(idea => {
    events.push({
      text: `发布了点子「${idea.title?.slice(0, 15)}」`,
      time: idea.created_at?.slice(0, 10) || '最近',
    });
    if (idea.likes_count > 0) {
      events.push({ text: `点子「${idea.title?.slice(0, 10)}」获得 ${idea.likes_count} 个赞`, time: '最近' });
    }
  });
  return events.slice(0, 8);
});

// 活跃度热力图数据
const activityDays = computed(() => {
  const days = [];
  for (let i = 34; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(0, 10);
    const count = myIdeas.value.filter(idea => idea.created_at?.slice(0, 10) === dateStr).length;
    const level = count === 0 ? 0 : count <= 1 ? 1 : count <= 3 ? 2 : 3;
    days.push({ date: dateStr, count, level });
  }
  return days;
});

function categoryIcon(cat) {
  const icons = { '时政': '🏛️', '财经': '💹', '科技': '🔬', '娱乐': '🎬', '体育': '⚽', '美食': '🍜', '教育': '📚', '其他': '📌' };
  return icons[cat] || '📌';
}

function statusType(status) {
  return status === 'approved' ? 'success' : status === 'rejected' ? 'danger' : 'warning';
}
function statusLabel(status) {
  return status === 'approved' ? '已通过' : status === 'rejected' ? '已拒绝' : '审核中';
}

async function load() {
  try {
    const [meRes, ideasRes] = await Promise.all([
      request.get('/auth/me'),
      request.get('/user/ideas'),
    ]);
    profile.value = meRes;
    selectedInterests.value = meRes.interests || [];
    editInterests.value = [...selectedInterests.value];
    myIdeas.value = ideasRes.items || [];
  } finally { loading.value = false; }
}

async function saveInterests() {
  const current = profile.value?.interests || [];
  for (const cat of current) {
    await request.delete(`/user/interests/${cat}`).catch(() => {});
  }
  for (const cat of editInterests.value) {
    await request.post('/user/interests', { category: cat }).catch(() => {});
  }
  ElMessage.success('偏好已更新');
  selectedInterests.value = [...editInterests.value];
  editing.value = false;
}

async function changePassword() {
  const valid = await pwdFormRef.value?.validate().catch(() => false);
  if (!valid) return;
  pwdLoading.value = true;
  try {
    await request.put('/user/password', {
      old_password: pwdForm.oldPwd,
      new_password: pwdForm.newPwd,
    });
    ElMessage.success('密码修改成功');
    pwdDialog.value = false;
    pwdForm.oldPwd = ''; pwdForm.newPwd = ''; pwdForm.confirmPwd = '';
  } catch {
  } finally {
    pwdLoading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.profile-page { width: 100%; }

/* Header */
.profile-header {
  background: var(--bg-card);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
.profile-banner {
  height: 120px;
  background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 50%, #6366f1 100%);
  position: relative;
}
.profile-banner::after {
  content: '';
  position: absolute; inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.profile-info {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 28px 24px;
  margin-top: -36px;
  position: relative;
}
.avatar-section { display: flex; align-items: flex-end; gap: 16px; }
.avatar-large {
  width: 72px; height: 72px;
  border-radius: 18px;
  background: linear-gradient(135deg, #6366f1, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; font-weight: 700; color: #fff;
  border: 4px solid #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,.15);
}
.user-meta { padding-bottom: 4px; }
.username { font-size: 22px; font-weight: 700; margin-bottom: 6px; }
.user-badges { display: flex; align-items: center; gap: 12px; }
.join-date { font-size: 13px; color: var(--text-secondary); }

/* Stats */
.stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-bottom: 20px; }
.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  display: flex; align-items: center; gap: 16px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  transition: all .2s;
}
.stat-card:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.stat-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px;
}
.stat-value { font-size: 26px; font-weight: 700; color: var(--text-primary); }
.stat-label { font-size: 13px; color: var(--text-secondary); margin-top: 2px; }

/* Grid - 3 columns */
.profile-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.left-col, .mid-col, .right-col { display: flex; flex-direction: column; gap: 20px; }

.section-card {}
.section-title {
  display: flex; align-items: center; gap: 8px;
  font-size: 16px; font-weight: 600;
}
.section-title .el-button { margin-left: auto; }

/* Interests */
.interest-tags { display: flex; flex-wrap: wrap; gap: 10px; }
.interest-tag {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  background: #eef2ff;
  border-radius: 20px;
  font-size: 14px; font-weight: 500; color: var(--primary);
  transition: all .2s;
}
.interest-tag:hover { background: #e0e7ff; }
.interest-icon { font-size: 16px; }
.interest-editor { padding: 8px 0; }
.editor-actions { display: flex; gap: 8px; margin-top: 12px; }

.empty-hint { text-align: center; padding: 16px 0; }
.empty-hint p { color: var(--text-secondary); margin-bottom: 8px; font-size: 14px; }

/* Achievement */
.achievement-grid { display: flex; flex-direction: column; gap: 10px; }
.achievement-item {
  display: flex; align-items: center; gap: 12px;
  padding: 12px; border-radius: var(--radius-sm);
  background: #f8fafc; transition: all .2s;
}
.achievement-item.unlocked { background: #f0fdf4; }
.ach-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.ach-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.ach-name { font-size: 14px; font-weight: 600; }
.ach-desc { font-size: 12px; color: var(--text-secondary); }

/* Security */
.security-list { display: flex; flex-direction: column; }
.security-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
}
.security-item:last-child { border-bottom: none; }
.security-info { display: flex; flex-direction: column; gap: 2px; }
.security-label { font-size: 14px; font-weight: 500; }
.security-desc { font-size: 12px; color: var(--text-secondary); }

/* Activity Chart */
.activity-chart {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 12px;
}
.activity-cell {
  aspect-ratio: 1;
  border-radius: 3px;
  transition: all .15s;
}
.activity-cell:hover { outline: 2px solid var(--primary); outline-offset: 1px; }
.level-0 { background: #f1f5f9; }
.level-1 { background: #c7d2fe; }
.level-2 { background: #818cf8; }
.level-3 { background: #4f46e5; }

.chart-legend { display: flex; align-items: center; gap: 4px; justify-content: flex-end; font-size: 12px; color: var(--text-secondary); }
.legend-cell { width: 14px; height: 14px; border-radius: 2px; }

/* Ideas list */
.ideas-list { display: flex; flex-direction: column; gap: 2px; }
.idea-card {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 0;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all .15s;
}
.idea-card:hover { padding-left: 8px; }
.idea-card:last-child { border-bottom: none; }
.idea-left { flex: 1; min-width: 0; }
.idea-title {
  font-size: 15px; font-weight: 500; margin-bottom: 6px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.idea-meta { display: flex; align-items: center; gap: 12px; font-size: 12px; color: var(--text-secondary); }

/* Browsing History */
.browsing-list { display: flex; flex-direction: column; gap: 2px; }
.browsing-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0; border-bottom: 1px solid #f1f5f9;
  cursor: pointer; transition: all .15s;
}
.browsing-item:hover { padding-left: 4px; }
.browsing-item:last-child { border-bottom: none; }
.browsing-icon { font-size: 16px; flex-shrink: 0; }
.browsing-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.browsing-title { font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.browsing-meta { font-size: 12px; color: var(--text-secondary); }

/* Data Overview */
.data-overview { display: flex; flex-direction: column; gap: 2px; }
.data-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0; border-bottom: 1px solid #f1f5f9;
}
.data-row:last-child { border-bottom: none; }
.data-label { font-size: 14px; color: var(--text-secondary); }
.data-value { font-size: 14px; font-weight: 600; color: var(--text-primary); }

/* Quick Actions */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.action-item {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  background: #f8fafc;
  cursor: pointer;
  transition: all .2s;
  font-size: 14px; font-weight: 500;
}
.action-item:hover { background: #eef2ff; transform: translateY(-1px); }
.action-icon {
  width: 40px; height: 40px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
}

/* Level */
.level-section {}
.level-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.level-name { font-size: 16px; font-weight: 700; color: var(--primary); }
.level-range { font-size: 13px; color: var(--text-secondary); }
.level-progress { margin-bottom: 14px; }
.level-exp { font-size: 12px; color: var(--text-secondary); display: block; text-align: right; margin-top: 4px; }
.level-perks { display: flex; flex-direction: column; gap: 6px; }
.perk-item { font-size: 13px; color: var(--text-secondary); }

/* Pref Analysis */
.pref-analysis { display: flex; flex-direction: column; gap: 10px; }
.pref-item {}
.pref-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; }
.pref-name { font-weight: 500; }
.pref-count { color: var(--text-secondary); }
.pref-track { height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden; }
.pref-fill { height: 100%; border-radius: 3px; transition: width .5s; }

/* Timeline */
.timeline-list { display: flex; flex-direction: column; gap: 2px; }
.timeline-item {
  display: flex; gap: 10px; padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}
.timeline-item:last-child { border-bottom: none; }
.timeline-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--primary); flex-shrink: 0; margin-top: 6px;
}
.timeline-content { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.timeline-text { font-size: 13px; }
.timeline-time { font-size: 11px; color: var(--text-secondary); }
</style>