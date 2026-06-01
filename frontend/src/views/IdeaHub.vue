<template>
  <div class="idea-page">
    <div class="page-header">
      <h2>💡 点子库</h2>
      <el-button type="primary" @click="$router.push('/ideas/create')">发布点子</el-button>
    </div>
    <div class="filters">
      <el-radio-group v-model="category" @change="fetchList" size="small">
        <el-radio-button label="">全部</el-radio-button>
        <el-radio-button v-for="cat in categories" :key="cat" :label="cat">{{ cat }}</el-radio-button>
      </el-radio-group>
      <el-radio-group v-model="sortBy" @change="fetchList" size="small" style="margin-left: auto">
        <el-radio-button label="hot">热门</el-radio-button><el-radio-button label="new">最新</el-radio-button>
      </el-radio-group>
    </div>
    <div class="card-grid" v-loading="loading">
      <el-card v-for="item in items" :key="item.id" class="idea-card" @click="$router.push(`/ideas/${item.id}`)">
        <h3>{{ item.title }}</h3>
        <div class="meta">
          <el-tag size="small">{{ item.category }}</el-tag>
          <span>{{ item.author_name }}</span>
          <span>👍 {{ item.likes_count }}</span>
          <span>💬 {{ item.comments_count }}</span>
        </div>
        <p class="preview">{{ item.content_preview }}</p>
      </el-card>
    </div>
    <el-empty v-if="!items.length && !loading" description="暂无点子" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '../api/request';

const items = ref([]);
const loading = ref(true);
const category = ref('');
const sortBy = ref('hot');
const categories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];

async function fetchList() {
  loading.value = true;
  try {
    const res = await request.get('/ideas', { params: { category: category.value || undefined, sort_by: sortBy.value } });
    items.value = res.data.items || [];
  } finally { loading.value = false; }
}

onMounted(fetchList);
</script>

<style scoped>
.idea-page { max-width: 900px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; }
.card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }
.idea-card { cursor: pointer; }
.idea-card h3 { font-size: 16px; margin-bottom: 8px; }
.meta { display: flex; gap: 12px; align-items: center; color: #909399; font-size: 13px; margin: 8px 0; }
.preview { color: #606266; font-size: 14px; line-height: 1.6; }
</style>
