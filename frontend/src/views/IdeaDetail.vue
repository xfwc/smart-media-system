<template>
  <div class="idea-detail" v-loading="loading">
    <el-button text @click="$router.back()">← 返回点子库</el-button>
    <h2>{{ idea?.title }}</h2>
    <div class="meta">
      <span>作者：{{ idea?.author?.username }}</span>
      <span>{{ idea?.created_at?.slice(0, 10) }}</span>
    </div>
    <div class="content">{{ idea?.content }}</div>
    <div class="actions">
      <el-button :type="idea?.liked_by_me ? 'danger' : 'default'" @click="toggleLike">
        {{ idea?.liked_by_me ? '❤️' : '🤍' }} {{ idea?.likes_count }}
      </el-button>
    </div>
    <h3>评论 ({{ idea?.comments?.length || 0 }})</h3>
    <div class="comment-input">
      <el-input v-model="commentText" placeholder="写下你的评论..." maxlength="500" show-word-limit>
        <template #append><el-button @click="submitComment">发布</el-button></template>
      </el-input>
    </div>
    <div v-for="c in idea?.comments" :key="c.id" class="comment-item">
      <strong>{{ c.author_name }}</strong>
      <span class="time">{{ c.created_at?.slice(0, 16) }}</span>
      <p>{{ c.content }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import request from '../api/request';

const route = useRoute();
const idea = ref(null);
const loading = ref(true);
const commentText = ref('');

async function load() {
  try {
    const res = await request.get(`/ideas/${route.params.id}`);
    idea.value = res.data;
  } finally { loading.value = false; }
}

async function toggleLike() {
  await request.post(`/ideas/${idea.value.id}/like`);
  load();
}

async function submitComment() {
  if (!commentText.value.trim()) return;
  await request.post(`/ideas/${idea.value.id}/comments`, { content: commentText.value });
  commentText.value = '';
  load();
}

onMounted(load);
</script>

<style scoped>
.idea-detail { max-width: 700px; margin: 0 auto; }
.meta { color: #909399; font-size: 14px; margin: 12px 0; display: flex; gap: 16px; }
.content { font-size: 15px; line-height: 1.8; margin: 20px 0; white-space: pre-wrap; }
.actions { margin: 16px 0; }
.comment-input { margin: 12px 0; }
.comment-item { padding: 12px 0; border-bottom: 1px solid #eee; }
.comment-item p { margin: 4px 0; }
.time { color: #909399; font-size: 12px; margin-left: 8px; }
</style>
