<template>
  <div class="hot-page">
    <div class="page-header">
      <h2>🔥 热榜分析</h2>
      <el-input v-model="keyword" placeholder="搜索热点..." style="width: 260px" clearable @change="fetchList" />
    </div>
    <div class="filters">
      <el-radio-group v-model="category" @change="fetchList" size="small">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</el-radio-button>
      </el-radio-group>
      <el-radio-group v-model="sortBy" @change="fetchList" size="small" style="margin-left: auto">
        <el-radio-button value="rank">按排名</el-radio-button>
        <el-radio-button value="heat">按热度</el-radio-button>
        <el-radio-button value="time">按时间</el-radio-button>
      </el-radio-group>
    </div>
    <el-table :data="items" stripe v-loading="loading" @row-click="goDetail" style="cursor: pointer">
      <el-table-column prop="rank" label="排名" width="70">
        <template #default="{ row }">
          <el-tag :type="row.rank <= 3 ? 'danger' : row.rank <= 10 ? 'warning' : 'info'" size="small">
            {{ row.rank }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="300" show-overflow-tooltip />
      <el-table-column prop="heat_value" label="热度" width="120">
        <template #default="{ row }">{{ formatHeat(row.heat_value) }}</template>
      </el-table-column>
      <el-table-column prop="category" label="分类" width="90">
        <template #default="{ row }"><el-tag size="small">{{ row.category || '-' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="日期" width="100">
        <template #default="{ row }">{{ row.collected_at?.slice(0, 10) || '-' }}</template>
      </el-table-column>
    </el-table>
    <el-pagination v-model:current-page="page" :total="total" :page-size="20" layout="prev, pager, next" @change="fetchList" style="margin-top: 20px; justify-content: center" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '../api/request';

const router = useRouter();
const items = ref([]);
const loading = ref(false);
const page = ref(1);
const total = ref(0);
const category = ref('');
const sortBy = ref('rank');
const keyword = ref('');
const categories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];

async function fetchList() {
  loading.value = true;
  try {
    const res = await request.get('/hot/list', { params: { page: page.value, category: category.value || undefined, sort_by: sortBy.value, keyword: keyword.value || undefined } });
    items.value = res.items || [];
    total.value = res.total || 0;
  } finally {
    loading.value = false;
  }
}

function goDetail(row) { router.push(`/hot/${row.id}`); }
function formatHeat(val) { return val > 10000 ? Math.round(val / 10000) + 'w' : val; }
onMounted(fetchList);
</script>

<style scoped>
.hot-page { max-width: 900px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.filters { display: flex; gap: 8px; margin-bottom: 16px; align-items: center; }
</style>
