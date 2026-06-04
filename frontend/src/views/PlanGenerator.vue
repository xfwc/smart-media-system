<template>
  <div class="plan-page">
    <!-- 步骤条 -->
    <el-card class="steps-card">
      <div class="custom-steps">
        <div class="step-item" :class="{ active: step === 0, done: step > 0 }">
          <div class="step-dot">
            <span v-if="step > 0">✓</span>
            <span v-else>1</span>
          </div>
          <div class="step-text">
            <span class="step-title">选择热点</span>
            <span class="step-desc">挑选感兴趣的话题</span>
          </div>
        </div>
        <div class="step-line" :class="{ active: step > 0 }"></div>
        <div class="step-item" :class="{ active: step === 1, done: step > 1 }">
          <div class="step-dot">
            <span v-if="step > 1">✓</span>
            <span v-else>2</span>
          </div>
          <div class="step-text">
            <span class="step-title">创作意图</span>
            <span class="step-desc">定制创作方向</span>
          </div>
        </div>
        <div class="step-line" :class="{ active: step > 1 }"></div>
        <div class="step-item" :class="{ active: step === 2, done: planStatus === 'completed' }">
          <div class="step-dot"><span>3</span></div>
          <div class="step-text">
            <span class="step-title">生成企划</span>
            <span class="step-desc">AI智能生成</span>
          </div>
        </div>
      </div>
    </el-card>

    <div class="plan-layout">
      <!-- 左侧主内容 -->
      <div class="plan-main">
        <!-- 步骤0：选择热点 -->
        <el-card v-if="step === 0" class="content-card">
          <h3 class="card-title">选择热点话题</h3>
          <div class="template-bar">
            <span class="template-label">快速模板：</span>
            <el-button v-for="t in templates" :key="t.name" size="small" round
              :type="selectedTemplate === t.name ? 'primary' : 'default'"
              @click="applyTemplate(t)">
              {{ t.icon }} {{ t.name }}
            </el-button>
          </div>
          <el-input v-model="topicSearch" placeholder="搜索热点..." prefix-icon="Search" style="margin-bottom: 16px" />
          <div class="topic-list">
            <div v-for="row in filteredTopics" :key="row.id" class="topic-item" @click="selectTopic(row)"
              :class="{ selected: selectedTopic?.id === row.id }">
              <div class="topic-info">
                <span class="topic-title">{{ row.title }}</span>
                <span class="topic-cat">{{ row.category }}</span>
              </div>
              <span class="topic-heat">🔥 {{ formatHeat(row.heat_value) }}</span>
            </div>
          </div>
        </el-card>

        <!-- 步骤1：创作意图 -->
        <el-card v-if="step === 1" class="content-card">
          <h3 class="card-title">定制你的创作方向</h3>
          <div class="selected-topic" v-if="selectedTopic">
            <span class="topic-badge">已选话题</span>
            <span>{{ selectedTopic.title }}</span>
          </div>
          <el-form label-position="top" class="intent-form">
            <el-form-item label="想表达的观点/角度">
              <el-input v-model="intent.angle" type="textarea" :rows="3" placeholder="例如：从创业者角度分析行业趋势" />
            </el-form-item>
            <el-form-item label="目标受众/粉丝画像">
              <el-input v-model="intent.audience" placeholder="例如：25-35岁职场人群" />
            </el-form-item>
            <el-form-item label="视频风格偏好">
              <el-select v-model="intent.style" placeholder="选择风格" style="width: 100%">
                <el-option label="知识科普" value="知识科普" />
                <el-option label="新闻评论" value="新闻评论" />
                <el-option label="生活教程" value="生活教程" />
                <el-option label="搞笑段子" value="搞笑段子" />
                <el-option label="深度分析" value="深度分析" />
                <el-option label="Vlog记录" value="Vlog记录" />
              </el-select>
            </el-form-item>
            <el-form-item label="预计时长">
              <el-radio-group v-model="intent.duration">
                <el-radio-button value="short">短视频 (&lt;1min)</el-radio-button>
                <el-radio-button value="medium">中视频 (1-5min)</el-radio-button>
                <el-radio-button value="long">长视频 (&gt;5min)</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="附加要求">
              <el-input v-model="intent.extra" type="textarea" :rows="2" placeholder="例如：需要加入数据图表展示" />
            </el-form-item>
          </el-form>
          <div class="step-actions">
            <el-button @click="step = 0" round>← 重新选择热点</el-button>
            <el-button type="primary" @click="step = 2" round>下一步：生成企划 →</el-button>
          </div>
        </el-card>

        <!-- 步骤2：生成企划 -->
        <el-card v-if="step === 2" class="content-card">
          <h3 class="card-title">生成企划案</h3>
          <div v-if="planStatus === 'loading'" class="loading-box">
            <div class="loading-spinner"></div>
            <h4>AI正在生成内容企划</h4>
            <p>正在根据你的创作意图，智能生成专属企划案...</p>
            <el-progress :percentage="genProgress" :stroke-width="8" :show-text="false" style="width: 300px; margin: 16px auto 0" />
          </div>
          <div v-else-if="planData" class="plan-result">
            <div class="result-toolbar">
              <el-button size="small" round @click="copyPlan">📋 复制企划</el-button>
              <el-button size="small" round @click="savePlan">💾 保存到历史</el-button>
            </div>
            <div class="result-section">
              <h4>📌 标题建议</h4>
              <div v-for="(t, i) in planData.title_suggestions" :key="i" class="title-item">
                <el-tag size="small" effect="plain" round>{{ t.style }}</el-tag>
                <span>{{ t.title }}</span>
                <el-button size="small" text type="primary" @click="copyText(t.title)">复制</el-button>
              </div>
            </div>

            <div class="result-section" v-if="planData.outline">
              <h4>📖 视频大纲</h4>
              <div class="outline-steps">
                <div class="outline-step">
                  <div class="outline-dot"></div>
                  <div class="outline-content">
                    <span class="outline-label">开头吸引</span>
                    <span class="outline-text">{{ planData.outline.hook }}</span>
                  </div>
                </div>
                <div class="outline-step">
                  <div class="outline-dot"></div>
                  <div class="outline-content">
                    <span class="outline-label">第一步</span>
                    <span class="outline-text">{{ planData.outline.step1 }}</span>
                  </div>
                </div>
                <div class="outline-step">
                  <div class="outline-dot"></div>
                  <div class="outline-content">
                    <span class="outline-label">第二步</span>
                    <span class="outline-text">{{ planData.outline.step2 }}</span>
                  </div>
                </div>
                <div class="outline-step">
                  <div class="outline-dot"></div>
                  <div class="outline-content">
                    <span class="outline-label">第三步</span>
                    <span class="outline-text">{{ planData.outline.step3 }}</span>
                  </div>
                </div>
                <div class="outline-step">
                  <div class="outline-dot"></div>
                  <div class="outline-content">
                    <span class="outline-label">结尾互动</span>
                    <span class="outline-text">{{ planData.outline.step4 }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="result-section">
              <h4>🎬 拍摄建议</h4>
              <p class="advice-text">{{ planData.advice?.shooting }}</p>
            </div>

            <div class="result-section">
              <h4>📅 发布建议</h4>
              <p class="advice-text">{{ planData.advice?.publishing }}</p>
            </div>

            <el-alert v-if="planData.risk_warning" :title="planData.risk_warning" type="warning" show-icon
              style="margin-top: 16px; border-radius: 8px;" />
          </div>
          <div v-else class="empty-state">
            <p>准备好后点击下方按钮开始生成</p>
          </div>
          <div class="step-actions">
            <el-button @click="step = 1" round>← 修改创作意图</el-button>
            <el-button type="primary" @click="generatePlan" :loading="planStatus === 'loading'" round>
              {{ planStatus === 'completed' ? '重新生成' : '开始生成' }}
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 右侧边栏 -->
      <div class="plan-sidebar">
        <!-- 创作小贴士 -->
        <div class="tips-card">
          <div class="sidebar-section-header">
            <span>💡</span> 创作小贴士
          </div>
          <div class="tips-list">
            <div class="tip-item" v-for="(tip, i) in tips" :key="i">
              <span class="tip-num">{{ i + 1 }}</span>
              <span class="tip-text">{{ tip }}</span>
            </div>
          </div>
        </div>

        <!-- 参考案例 -->
        <div class="sidebar-card">
          <div class="sidebar-section-header">
            <span>📖</span> 参考案例
          </div>
          <div class="case-list">
            <div v-for="(c, i) in refCases" :key="i" class="case-item" @click="showCase(c)">
              <div class="case-header">
                <el-tag size="small" :type="c.type" effect="plain" round>{{ c.style }}</el-tag>
                <span class="case-views">👁 {{ c.views }}</span>
              </div>
              <span class="case-title">{{ c.title }}</span>
              <div class="case-meta">
                <span>👍 {{ c.likes }}</span>
                <span>⭐ {{ c.score }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 同话题企划 -->
        <div class="sidebar-card" v-if="selectedTopic">
          <div class="sidebar-section-header">
            <span>🔗</span> 同话题企划
          </div>
          <div class="similar-list">
            <div v-for="(s, i) in similarPlans" :key="i" class="similar-item">
              <span class="similar-title">{{ s.title }}</span>
              <div class="similar-meta">
                <el-tag size="small" effect="plain" round>{{ s.style }}</el-tag>
                <span class="similar-score">匹配 {{ s.match }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史企划 -->
        <div class="sidebar-card">
          <div class="sidebar-section-header">
            <span>📚</span> 历史企划
            <el-button v-if="planHistory.length" size="small" text type="danger" @click="clearHistory">清空</el-button>
          </div>
          <div v-if="planHistory.length" class="history-list">
            <div v-for="(h, i) in planHistory" :key="i" class="history-item" @click="loadHistory(h)">
              <div class="history-topic">{{ h.topicTitle }}</div>
              <div class="history-meta">
                <span>{{ h.style }}</span>
                <span>{{ h.time }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-history">暂无历史企划</div>
        </div>
      </div>
    </div>

    <!-- 案例详情对话框 -->
    <el-dialog v-model="caseDialogVisible" :title="currentCase?.title" width="500px">
      <div v-if="currentCase" class="case-detail">
        <div class="case-detail-meta">
          <el-tag :type="currentCase.type" effect="plain" round>{{ currentCase.style }}</el-tag>
          <span>👁 {{ currentCase.views }} 次观看</span>
          <span>👍 {{ currentCase.likes }} 点赞</span>
        </div>
        <div class="case-detail-section">
          <h4>📝 企划摘要</h4>
          <p>{{ currentCase.summary }}</p>
        </div>
        <div class="case-detail-section">
          <h4>🎯 核心要点</h4>
          <ul>
            <li v-for="(point, i) in currentCase.points" :key="i">{{ point }}</li>
          </ul>
        </div>
        <div class="case-detail-footer">
          <el-button type="primary" round @click="applyCase">应用到当前企划</el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const route = useRoute();
const step = ref(0);
const topicSearch = ref('');
const topics = ref([]);
const selectedTopic = ref(null);
const selectedTemplate = ref('');
const intent = reactive({ angle: '', audience: '', style: '', duration: 'medium', extra: '' });
const planStatus = ref('');
const planData = ref(null);
const genProgress = ref(0);
const caseDialogVisible = ref(false);
const currentCase = ref(null);

const templates = [
  { name: '科普解析', icon: '🔬', style: '知识科普', angle: '以通俗易懂的方式解析专业概念', audience: '对科技感兴趣的大众', duration: 'medium' },
  { name: '热点评论', icon: '📰', style: '新闻评论', angle: '从独特视角发表观点和见解', audience: '关注时事的成年人', duration: 'short' },
  { name: '教程干货', icon: '📖', style: '生活教程', angle: '手把手教实用技能', audience: '想学习的入门者', duration: 'long' },
  { name: '深度分析', icon: '🔍', style: '深度分析', angle: '用数据和逻辑深入剖析', audience: '行业从业者', duration: 'long' },
];

const tips = [
  '选择你熟悉领域的热点，创作更得心应手',
  '开头3秒决定观众是否继续观看',
  '加入个人观点能让内容更有辨识度',
  '结尾引导互动可以提高完播率',
  '发布时间建议选择晚上7-10点',
  '标题带数字和疑问句更吸引点击',
  '每2-3分钟设置一个高潮点保持注意力',
];

// 参考案例
const refCases = ref([
  { title: '如何用3分钟讲透一个科技概念', style: '知识科普', type: '', views: '12.3w', likes: 892, score: 95,
    summary: '以通俗易懂的语言拆解复杂的科技概念，配合动画演示，让观众在3分钟内理解核心原理。',
    points: ['开头用生活场景引入问题', '核心概念用类比解释', '结尾留下思考问题'] },
  { title: '热点事件深度解读：背后真相', style: '深度分析', type: 'success', views: '8.7w', likes: 654, score: 91,
    summary: '从多角度深度解读热点事件，提供独到见解，用数据支撑观点，引导观众独立思考。',
    points: ['梳理事件时间线', '收集多方观点对比', '给出个人深度解读'] },
  { title: '手把手教你做出爆款短视频', style: '生活教程', type: 'warning', views: '15.1w', likes: 1203, score: 88,
    summary: '从选题、脚本到剪辑的全流程教程，适合新手入门，步骤清晰，可操作性强。',
    points: ['选题技巧和工具推荐', '脚本模板直接套用', '剪辑软件实操演示'] },
  { title: '今日热点辣评：别被带节奏', style: '新闻评论', type: 'danger', views: '22.5w', likes: 2341, score: 92,
    summary: '犀利点评当日热点，揭露信息差，帮助观众看清事件本质，保持独立思考。',
    points: ['快速梳理事件核心', '指出常见认知误区', '给出理性分析框架'] },
]);

// 同话题企划
const similarPlans = computed(() => {
  if (!selectedTopic.value) return [];
  const styles = ['知识科普', '新闻评论', '生活教程', '深度分析'];
  return styles.map((style, i) => ({
    title: `关于「${selectedTopic.value.title?.slice(0, 15) || '话题'}」的${style}企划`,
    style,
    match: 90 - i * 8 + Math.floor(Math.random() * 5),
  })).sort((a, b) => b.match - a.match);
});

let searchTimer = null;
let progressTimer = null;

// 历史企划
const planHistory = ref(JSON.parse(localStorage.getItem('plan_history') || '[]'));

function savePlan() {
  if (!planData.value || !selectedTopic.value) return;
  planHistory.value.unshift({
    topicTitle: selectedTopic.value.title,
    style: intent.style || '未设定',
    time: new Date().toLocaleString('zh-CN'),
    data: planData.value,
    intent: { ...intent },
  });
  if (planHistory.value.length > 20) planHistory.value = planHistory.value.slice(0, 20);
  localStorage.setItem('plan_history', JSON.stringify(planHistory.value));
  ElMessage.success('已保存到历史');
}

function loadHistory(h) {
  planData.value = h.data;
  planStatus.value = 'completed';
  step.value = 2;
}

function clearHistory() {
  planHistory.value = [];
  localStorage.removeItem('plan_history');
  ElMessage.success('历史已清空');
}

// 模板
function applyTemplate(t) {
  selectedTemplate.value = t.name;
  intent.style = t.style;
  intent.angle = t.angle;
  intent.audience = t.audience;
  intent.duration = t.duration;
  ElMessage.success(`已应用「${t.name}」模板`);
}

// 案例查看
function showCase(c) {
  currentCase.value = c;
  caseDialogVisible.value = true;
}
function applyCase() {
  if (currentCase.value) {
    intent.style = currentCase.value.style;
    intent.angle = currentCase.value.points?.[0] || '';
    ElMessage.success('已参考该案例风格');
    caseDialogVisible.value = false;
  }
}

// 复制
function copyPlan() {
  const text = JSON.stringify(planData.value, null, 2);
  navigator.clipboard?.writeText(text);
  ElMessage.success('企划内容已复制');
}
function copyText(text) {
  navigator.clipboard?.writeText(text);
  ElMessage.success('已复制');
}

const filteredTopics = computed(() => {
  if (!topicSearch.value) return topics.value;
  return topics.value.filter(t => t.title.includes(topicSearch.value));
});

async function loadTopics(keyword = '') {
  const tid = route.query.topic_id;
  const res = await request.get('/hot/list', { params: { page_size: 50, keyword: keyword || undefined } });
  topics.value = res.items || [];
  if (tid && !keyword) {
    selectedTopic.value = topics.value.find(t => t.id == tid) || null;
    if (selectedTopic.value) step.value = 1;
  }
}

watch(topicSearch, (val) => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadTopics(val), 300);
});

function formatHeat(val) { return val > 10000 ? Math.round(val / 10000) + 'w' : val; }

function selectTopic(row) {
  selectedTopic.value = row;
  step.value = 1;
}

async function generatePlan() {
  if (!selectedTopic.value) return;
  planStatus.value = 'loading';
  genProgress.value = 0;
  clearInterval(progressTimer);
  progressTimer = setInterval(() => {
    if (genProgress.value < 90) genProgress.value += Math.random() * 15;
  }, 1000);
  try {
    const res = await request.post('/plan/generate', {
      topic_id: selectedTopic.value.id,
      intent: intent.angle || intent.audience || intent.style ? intent : undefined,
    });
    const planId = res.plan_id;
    let retries = 15;
    while (retries-- > 0) {
      await new Promise(r => setTimeout(r, 2000));
      const statusRes = await request.get(`/plan/${planId}/status`);
      if (statusRes.status === 'completed') {
        planData.value = statusRes.data;
        planStatus.value = 'completed';
        genProgress.value = 100;
        clearInterval(progressTimer);
        return;
      }
    }
    planStatus.value = 'timeout';
    clearInterval(progressTimer);
  } catch {
    planStatus.value = 'failed';
    clearInterval(progressTimer);
  }
}

onMounted(loadTopics);
</script>

<style scoped>
.plan-page { width: 100%; }

/* Steps */
.steps-card { margin-bottom: 20px; }
.custom-steps { display: flex; align-items: flex-start; }
.step-item { display: flex; align-items: flex-start; gap: 12px; }
.step-dot {
  width: 36px; height: 36px; flex-shrink: 0;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
  background: #f1f5f9; color: var(--text-secondary);
  border: 2px solid #e2e8f0;
  transition: all .3s;
}
.step-item.active .step-dot {
  background: var(--primary); color: #fff; border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(99,102,241,.15);
}
.step-item.done .step-dot { background: #10b981; color: #fff; border-color: #10b981; }
.step-text { display: flex; flex-direction: column; gap: 2px; padding-top: 2px; }
.step-title { font-size: 14px; font-weight: 600; color: var(--text-secondary); }
.step-item.active .step-title { color: var(--text-primary); }
.step-item.done .step-title { color: var(--text-primary); }
.step-desc { font-size: 12px; color: #94a3b8; }
.step-line {
  flex: 1; height: 2px; background: #e2e8f0;
  margin: 18px 16px 0; min-width: 40px; border-radius: 1px;
  transition: background .3s;
}
.step-line.active { background: var(--primary); }

/* Layout */
.plan-layout { display: grid; grid-template-columns: 1fr 320px; gap: 20px; }
.plan-main { min-width: 0; }
.plan-sidebar { display: flex; flex-direction: column; gap: 16px; }

/* Content */
.content-card { min-height: 300px; }
.card-title { font-size: 18px; font-weight: 600; margin-bottom: 16px; }

.template-bar { display: flex; align-items: center; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.template-label { font-size: 13px; color: var(--text-secondary); font-weight: 500; }

.topic-list { max-height: 400px; overflow-y: auto; }
.topic-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px; border-radius: var(--radius-sm);
  cursor: pointer; transition: all .2s;
  border: 1px solid transparent;
}
.topic-item:hover { background: #f8fafc; border-color: #e2e8f0; }
.topic-item.selected { background: #eef2ff; border-color: var(--primary); }
.topic-info { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.topic-title { font-size: 14px; font-weight: 500; }
.topic-cat { font-size: 12px; color: var(--text-secondary); }
.topic-heat { font-size: 13px; color: #f59e0b; font-weight: 500; flex-shrink: 0; }

.selected-topic {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; background: #eef2ff;
  border-radius: var(--radius-sm); margin-bottom: 20px;
  font-size: 14px; font-weight: 500;
}
.topic-badge {
  background: var(--primary); color: #fff;
  padding: 2px 10px; border-radius: 10px;
  font-size: 12px; font-weight: 600;
}

.intent-form { margin-bottom: 8px; }
.step-actions { display: flex; gap: 12px; justify-content: flex-end; padding-top: 8px; }

/* Loading */
.loading-box { text-align: center; padding: 48px 0; }
.loading-spinner {
  width: 48px; height: 48px; margin: 0 auto 16px;
  border: 3px solid #e2e8f0; border-top-color: var(--primary);
  border-radius: 50%; animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-box h4 { font-size: 16px; margin-bottom: 6px; }
.loading-box p { color: var(--text-secondary); font-size: 14px; }

.empty-state { text-align: center; padding: 40px 0; color: var(--text-secondary); }

/* Result */
.plan-result { display: flex; flex-direction: column; gap: 24px; }
.result-toolbar { display: flex; gap: 8px; justify-content: flex-end; }
.result-section h4 { font-size: 15px; font-weight: 600; margin-bottom: 12px; color: var(--text-primary); }
.title-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; background: #f8fafc; border-radius: var(--radius-sm);
  margin-bottom: 8px; font-size: 14px;
}
.title-item .el-button { margin-left: auto; }

.outline-steps { display: flex; flex-direction: column; gap: 0; position: relative; padding-left: 20px; }
.outline-step {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 12px 0; position: relative;
}
.outline-dot {
  width: 12px; height: 12px; flex-shrink: 0;
  border-radius: 50%; background: var(--primary);
  margin-top: 4px; position: relative;
  box-shadow: 0 0 0 4px rgba(99,102,241,.15);
}
.outline-step:not(:last-child)::before {
  content: ''; position: absolute;
  left: 5px; top: 28px; bottom: -12px;
  width: 2px; background: #e2e8f0;
}
.outline-content { display: flex; flex-direction: column; gap: 2px; }
.outline-label { font-size: 12px; color: var(--text-secondary); }
.outline-text { font-size: 14px; font-weight: 500; }
.advice-text { font-size: 14px; line-height: 1.8; color: var(--text-primary); }

/* Sidebar cards */
.tips-card, .sidebar-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
.sidebar-section-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600; margin-bottom: 16px;
}
.sidebar-section-header .el-button { margin-left: auto; }

.tips-list { display: flex; flex-direction: column; gap: 10px; }
.tip-item { display: flex; gap: 10px; align-items: flex-start; }
.tip-num {
  width: 22px; height: 22px; border-radius: 50%; flex-shrink: 0;
  background: #eef2ff; color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
}
.tip-text { font-size: 13px; line-height: 1.6; color: var(--text-secondary); }

/* Reference Cases */
.case-list { display: flex; flex-direction: column; gap: 10px; }
.case-item {
  padding: 12px; border-radius: var(--radius-sm);
  background: #f8fafc; cursor: pointer; transition: all .2s;
}
.case-item:hover { background: #eef2ff; }
.case-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.case-views { font-size: 12px; color: var(--text-secondary); }
.case-title { font-size: 14px; font-weight: 500; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.case-meta { display: flex; gap: 12px; margin-top: 6px; font-size: 12px; color: var(--text-secondary); }

/* Similar Plans */
.similar-list { display: flex; flex-direction: column; gap: 8px; }
.similar-item {
  padding: 10px; border-radius: var(--radius-sm);
  background: #f8fafc; cursor: pointer; transition: all .2s;
}
.similar-item:hover { background: #eef2ff; }
.similar-title { font-size: 13px; font-weight: 500; display: block; margin-bottom: 6px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.similar-meta { display: flex; align-items: center; justify-content: space-between; }
.similar-score { font-size: 12px; font-weight: 600; color: var(--primary); }

.history-list { display: flex; flex-direction: column; gap: 2px; }
.history-item {
  padding: 12px; border-radius: var(--radius-sm);
  cursor: pointer; transition: all .15s;
}
.history-item:hover { background: #f8fafc; }
.history-topic { font-size: 14px; font-weight: 500; margin-bottom: 4px; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
.history-meta { display: flex; gap: 12px; font-size: 12px; color: var(--text-secondary); }
.no-history { text-align: center; padding: 20px 0; color: var(--text-secondary); font-size: 14px; }

/* Case Detail */
.case-detail-meta { display: flex; gap: 12px; align-items: center; margin-bottom: 16px; font-size: 13px; color: var(--text-secondary); }
.case-detail-section { margin-bottom: 16px; }
.case-detail-section h4 { font-size: 14px; font-weight: 600; margin-bottom: 8px; }
.case-detail-section p { font-size: 14px; line-height: 1.8; color: var(--text-secondary); }
.case-detail-section ul { padding-left: 20px; }
.case-detail-section li { font-size: 14px; line-height: 2; color: var(--text-secondary); }
.case-detail-footer { text-align: center; padding-top: 8px; }
</style>