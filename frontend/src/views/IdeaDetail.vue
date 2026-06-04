<template>
  <div class="idea-detail" v-loading="loading">
    <div class="back-btn" @click="$router.back()">
      <span class="back-arrow">←</span> 返回点子库
    </div>

    <div class="detail-layout" v-if="idea">
      <!-- 主内容 -->
      <div class="main-content">
        <el-card class="content-card">
          <h1 class="idea-title">{{ idea.title }}</h1>
          <div class="meta-row">
            <div class="author-info">
              <div class="author-avatar">{{ idea.author?.username?.charAt(0) }}</div>
              <span class="author-name">{{ idea.author?.username }}</span>
            </div>
            <span class="meta-date">{{ idea.created_at?.slice(0, 10) }}</span>
            <el-tag v-if="idea.category" size="small" effect="plain" round>{{ idea.category }}</el-tag>
            <el-tag v-if="idea.status" :type="idea.status === 'approved' ? 'success' : idea.status === 'rejected' ? 'danger' : 'warning'" size="small" effect="dark" round>
              {{ idea.status === 'approved' ? '已通过' : idea.status === 'rejected' ? '已拒绝' : '审核中' }}
            </el-tag>
          </div>

          <!-- 标签 -->
          <div class="idea-tags" v-if="idea.tags?.length">
            <el-tag v-for="tag in idea.tags" :key="tag" size="small" type="info" effect="plain" round>{{ tag }}</el-tag>
          </div>

          <div class="idea-content">{{ idea.content }}</div>

          <div class="action-bar">
            <el-button :type="idea.liked_by_me ? 'danger' : 'default'" round @click="toggleLike">
              {{ idea.liked_by_me ? '❤️' : '🤍' }} {{ idea.likes_count }} 赞
            </el-button>
            <el-button :type="isFavorite ? 'warning' : 'default'" round @click="toggleFavorite">
              {{ isFavorite ? '⭐ 已收藏' : '☆ 收藏' }}
            </el-button>
            <el-button round @click="shareIdea">🔗 分享</el-button>
            <el-button round @click="goCreatePlan">📝 生成企划</el-button>
          </div>
        </el-card>

        <!-- 评论区 -->
        <el-card class="comment-card">
          <h3 class="comment-title">评论 ({{ idea.comments?.length || 0 }})</h3>
          <div class="comment-input">
            <el-input v-model="commentText" placeholder="写下你的评论..." maxlength="500" show-word-limit>
              <template #append>
                <el-button @click="submitComment" type="primary">发布</el-button>
              </template>
            </el-input>
          </div>
          <div v-for="c in idea.comments" :key="c.id" class="comment-item">
            <div class="comment-header">
              <div class="comment-author">
                <div class="comment-avatar">{{ c.author_name?.charAt(0) }}</div>
                <strong>{{ c.author_name }}</strong>
              </div>
              <span class="comment-time">{{ c.created_at?.slice(0, 16) }}</span>
            </div>
            <p class="comment-text">{{ c.content }}</p>
          </div>
          <el-empty v-if="!idea.comments?.length" description="暂无评论，来发表第一条吧" :image-size="60" />
        </el-card>
      </div>

      <!-- 侧边栏 -->
      <div class="sidebar">
        <!-- 作者信息卡 -->
        <div class="author-card" v-if="idea.author">
          <div class="author-card-header">
            <div class="author-avatar-lg">{{ idea.author.username?.charAt(0) }}</div>
            <div>
              <div class="author-name-lg">{{ idea.author.username }}</div>
              <el-tag v-if="idea.author.role" size="small" :type="idea.author.role === 'admin' ? 'danger' : 'primary'" effect="dark" round>
                {{ idea.author.role === 'admin' ? '管理员' : '创作者' }}
              </el-tag>
            </div>
          </div>
          <div class="author-stats">
            <div class="author-stat">
              <span class="author-stat-val">{{ idea.author.ideas_count || 0 }}</span>
              <span class="author-stat-label">点子</span>
            </div>
            <div class="author-stat">
              <span class="author-stat-val">{{ idea.author.likes_total || 0 }}</span>
              <span class="author-stat-label">获赞</span>
            </div>
          </div>
        </div>

        <!-- 相关推荐 -->
        <div class="related-card">
          <div class="sidebar-header">🔗 相关点子</div>
          <div v-for="r in relatedIdeas" :key="r.id" class="related-item" @click="$router.push(`/ideas/${r.id}`)">
            <h4 class="related-title">{{ r.title }}</h4>
            <div class="related-meta">
              <span>👍 {{ r.likes_count }}</span>
              <span>💬 {{ r.comments_count }}</span>
              <el-tag size="small" effect="plain" round>{{ r.category }}</el-tag>
            </div>
          </div>
          <div v-if="!relatedIdeas.length" class="no-data">暂无相关点子</div>
        </div>
      </div>
    </div>

    <!-- 分享对话框 -->
    <el-dialog v-model="shareDialog" title="分享点子" width="440px">
      <div class="share-content">
        <el-input :model-value="shareUrl" readonly>
          <template #append>
            <el-button @click="copyUrl">复制</el-button>
          </template>
        </el-input>
        <div class="share-channels">
          <div class="share-channel" @click="shareTo('wechat')">
            <div class="channel-icon" style="background: #07c160;">微</div>
            <span>微信</span>
          </div>
          <div class="share-channel" @click="shareTo('weibo')">
            <div class="channel-icon" style="background: #e6162d;">博</div>
            <span>微博</span>
          </div>
          <div class="share-channel" @click="shareTo('qq')">
            <div class="channel-icon" style="background: #12b7f5;">Q</div>
            <span>QQ</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const route = useRoute();
const router = useRouter();
const idea = ref(null);
const loading = ref(true);
const commentText = ref('');
const shareDialog = ref(false);
const relatedIdeas = ref([]);

// 收藏
const favorites = ref(JSON.parse(localStorage.getItem('idea_favorites') || '[]'));
const isFavorite = computed(() => idea.value ? favorites.value.includes(idea.value.id) : false);
function toggleFavorite() {
  if (!idea.value) return;
  const idx = favorites.value.indexOf(idea.value.id);
  if (idx >= 0) { favorites.value.splice(idx, 1); ElMessage.success('已取消收藏'); }
  else { favorites.value.push(idea.value.id); ElMessage.success('已收藏'); }
  localStorage.setItem('idea_favorites', JSON.stringify(favorites.value));
}

// 分享
const shareUrl = computed(() => window.location.href);
function shareIdea() { shareDialog.value = true; }
function copyUrl() { navigator.clipboard?.writeText(shareUrl.value); ElMessage.success('链接已复制'); }
function shareTo(ch) { ElMessage.success(`已分享到${ch === 'wechat' ? '微信' : ch === 'weibo' ? '微博' : 'QQ'}`); shareDialog.value = false; }

function goCreatePlan() {
  router.push({ path: '/plan', query: { topic_title: idea.value?.title } });
}

async function load() {
  try {
    const res = await request.get(`/ideas/${route.params.id}`);
    idea.value = res;
    // 加载相关点子
    try {
      const listRes = await request.get('/ideas', { params: { category: res.category, sort_by: 'hot' } });
      relatedIdeas.value = (listRes.items || []).filter(i => i.id != route.params.id).slice(0, 5);
    } catch {}
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
.idea-detail { width: 100%; }

.back-btn {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--primary); font-size: 14px; font-weight: 500;
  cursor: pointer; margin-bottom: 20px;
  padding: 6px 14px; border-radius: 8px;
  transition: background .2s;
}
.back-btn:hover { background: #eef2ff; }
.back-arrow { font-size: 18px; }

.detail-layout { display: grid; grid-template-columns: 1fr 300px; gap: 20px; }
.main-content { display: flex; flex-direction: column; gap: 16px; }
.sidebar { display: flex; flex-direction: column; gap: 16px; }

.content-card { margin-bottom: 0; }
.idea-title { font-size: 22px; font-weight: 700; margin-bottom: 16px; line-height: 1.4; }

.meta-row { display: flex; align-items: center; gap: 16px; margin-bottom: 16px; flex-wrap: wrap; }
.author-info { display: flex; align-items: center; gap: 8px; }
.author-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 600; color: #fff;
}
.author-name { font-size: 14px; font-weight: 500; }
.meta-date { font-size: 13px; color: var(--text-secondary); }

.idea-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }

.idea-content {
  font-size: 15px; line-height: 1.9; margin: 20px 0;
  white-space: pre-wrap; color: var(--text-primary);
}

.action-bar { display: flex; gap: 8px; padding-top: 16px; border-top: 1px solid #f1f5f9; flex-wrap: wrap; }

/* Comments */
.comment-card {}
.comment-title { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.comment-input { margin-bottom: 20px; }
.comment-item { padding: 16px 0; border-bottom: 1px solid #f1f5f9; }
.comment-item:last-child { border-bottom: none; }
.comment-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.comment-author { display: flex; align-items: center; gap: 8px; }
.comment-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 600; color: #fff;
}
.comment-time { font-size: 12px; color: #94a3b8; }
.comment-text { font-size: 14px; line-height: 1.7; color: var(--text-primary); }

/* Author card */
.author-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
.author-card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 16px; }
.author-avatar-lg {
  width: 48px; height: 48px; border-radius: 14px;
  background: linear-gradient(135deg, #6366f1, #a78bfa);
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 700; color: #fff;
}
.author-name-lg { font-size: 16px; font-weight: 600; margin-bottom: 4px; }
.author-stats { display: flex; gap: 24px; padding-top: 12px; border-top: 1px solid #f1f5f9; }
.author-stat { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.author-stat-val { font-size: 20px; font-weight: 700; color: var(--primary); }
.author-stat-label { font-size: 12px; color: var(--text-secondary); }

/* Related card */
.related-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}
.sidebar-header { font-size: 15px; font-weight: 600; margin-bottom: 14px; }
.related-item { padding: 12px 0; border-bottom: 1px solid #f1f5f9; cursor: pointer; transition: all .15s; }
.related-item:hover { padding-left: 6px; }
.related-item:last-child { border-bottom: none; }
.related-title { font-size: 14px; font-weight: 500; margin-bottom: 6px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.related-meta { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--text-secondary); }
.no-data { text-align: center; padding: 20px 0; color: var(--text-secondary); font-size: 14px; }

/* Share dialog */
.share-content { display: flex; flex-direction: column; gap: 20px; }
.share-channels { display: flex; gap: 24px; justify-content: center; }
.share-channel { display: flex; flex-direction: column; align-items: center; gap: 6px; cursor: pointer; }
.channel-icon {
  width: 44px; height: 44px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 700; font-size: 18px;
  transition: transform .2s;
}
.share-channel:hover .channel-icon { transform: scale(1.1); }
.share-channel span { font-size: 12px; color: var(--text-secondary); }
</style>
