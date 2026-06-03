<template>
  <div class="plan-page">
    <h2>📝 内容企划生成</h2>
    <el-card style="max-width: 800px; margin: 0 auto">
      <div class="custom-steps">
        <div class="step-item" :class="{ active: step === 0, done: step > 0 }">
          <span class="dot"></span>
          <span class="step-title">选择热点</span>
        </div>
        <div class="step-line" :class="{ dark: step > 0 }"></div>
        <div class="step-item" :class="{ active: step === 1, done: step > 1 }">
          <span class="dot"></span>
          <span class="step-title">创作意图</span>
        </div>
        <div class="step-line" :class="{ dark: step > 1 }"></div>
        <div class="step-item" :class="{ active: step === 2 }">
          <span class="dot"></span>
          <span class="step-title">生成企划</span>
        </div>
      </div>

      <div v-if="step === 0">
        <h3>选择热点话题</h3>
        <el-input v-model="topicSearch" placeholder="搜索热点..." style="margin-bottom: 12px" />
        <el-table :data="topics" @row-click="selectTopic" highlight-current-row height="300" :show-header="false">
          <el-table-column show-overflow-tooltip>
            <template #default="{ row }"><div class="topic-row"><span>{{ row.title }}</span><span class="heat-tag">{{ formatHeat(row.heat_value) }}</span></div></template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="step === 1">
        <h3>定制你的创作方向</h3>
        <el-form label-position="top">
          <el-form-item label="想表达的观点/角度">
            <el-input v-model="intent.angle" type="textarea" :rows="3" placeholder="例如：从创业者角度分析行业趋势" />
          </el-form-item>
          <el-form-item label="目标受众/粉丝画像">
            <el-input v-model="intent.audience" placeholder="例如：25-35岁职场人群" />
          </el-form-item>
          <el-form-item label="视频风格偏好">
            <el-select v-model="intent.style" placeholder="选择风格">
              <el-option label="知识科普" value="知识科普" /><el-option label="新闻评论" value="新闻评论" /><el-option label="生活教程" value="生活教程" />
            </el-select>
          </el-form-item>
        </el-form>
        <div class="step-actions">
          <el-button @click="step = 0">上一步：重新选择热点</el-button>
          <el-button type="primary" @click="step = 2">下一步：生成企划</el-button>
        </div>
      </div>

      <div v-if="step === 2">
        <h3>生成企划案</h3>
        <div v-if="planStatus === 'loading'" style="text-align: center; padding: 40px">
          <el-icon class="is-loading" :size="40"><Loading /></el-icon>
          <p>AI正在生成内容企划，请稍候...</p>
        </div>
        <div v-else-if="planData">
          <h4>📌 标题建议</h4>
          <div v-for="(t, i) in planData.title_suggestions" :key="i" class="title-item">
            <el-tag size="small">{{ t.style }}</el-tag> {{ t.title }}
          </div>
          <h4 style="margin-top: 16px">📖 视频大纲</h4>
          <div v-if="planData.outline">
            <el-steps direction="vertical">
              <el-step :title="planData.outline.hook" description="开头吸引" />
              <el-step :title="planData.outline.step1" description="第一步" />
              <el-step :title="planData.outline.step2" description="第二步" />
              <el-step :title="planData.outline.step3" description="第三步" />
              <el-step :title="planData.outline.step4" description="结尾互动" />
            </el-steps>
          </div>
          <h4 style="margin-top: 16px">🎬 拍摄建议</h4>
          <p>{{ planData.advice?.shooting }}</p>
          <h4>📅 发布建议</h4>
          <p>{{ planData.advice?.publishing }}</p>
          <el-alert v-if="planData.risk_warning" :title="planData.risk_warning" type="warning" show-icon style="margin-top: 12px" />
        </div>
        <div class="step-actions">
          <el-button @click="step = 1">上一步：修改创作意图</el-button>
          <el-button type="primary" @click="generatePlan" :loading="planStatus === 'loading'">开始生成</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import request from '../api/request';
import { Loading } from '@element-plus/icons-vue';

const route = useRoute();
const step = ref(0);
const topicSearch = ref('');
const topics = ref([]);
const selectedTopic = ref(null);
const intent = reactive({ angle: '', audience: '', style: '' });
const planStatus = ref('');
const planData = ref(null);

let searchTimer = null;

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
        return;
      }
    }
    planStatus.value = 'timeout';
  } catch {
    planStatus.value = 'failed';
  }
}

onMounted(loadTopics);
</script>

<style scoped>
.plan-page { max-width: 900px; margin: 0 auto; }
.title-item { padding: 8px 0; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 8px; }
.step-actions { display: flex; gap: 12px; margin-top: 16px; justify-content: flex-end; }

.custom-steps { display: flex; align-items: center; margin-bottom: 24px; padding: 0 20px; }
.step-item { display: flex; align-items: center; gap: 8px; flex: 0 0 auto; }
.step-item .dot {
  width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0;
  border: 2px solid #c0c4cc; background: #fff;
}
.step-item.active .dot { background: #303133; border-color: #303133; }
.step-item.done .dot { background: #409eff; border-color: #409eff; }
.step-title { font-size: 14px; white-space: nowrap; }
.step-item .step-title { color: #c0c4cc; }
.step-item.active .step-title { color: #303133; font-weight: 700; }
.step-item.done .step-title { color: #303133; font-weight: 700; }
.step-line { flex: 1 1 auto; height: 2px; background: #e4e7ed; margin: 0 12px; min-width: 30px; }
.step-line.dark { background: #909399; }
.topic-row { display: flex; align-items: center; width: 100%; }
.heat-tag { font-size: 12px; color: #909399; margin-left: auto; flex-shrink: 0; }
</style>
