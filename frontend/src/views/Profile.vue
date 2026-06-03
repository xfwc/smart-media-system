<template>
  <div class="profile-page" v-loading="loading">
    <h2>个人中心</h2>
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>账号信息</template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="用户名">{{ profile?.username }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ profile?.email || '未设置' }}</el-descriptions-item>
            <el-descriptions-item label="角色">{{ profile?.role === 'admin' ? '管理员' : '创作者' }}</el-descriptions-item>
            <el-descriptions-item label="密码">
              <el-button type="primary" link size="small" @click="pwdDialog = true">修改密码</el-button>
            </el-descriptions-item>
          </el-descriptions>

          <h4 style="margin: 20px 0 10px">关注领域偏好</h4>
          <template v-if="!editing">
            <div class="categories">
              <el-tag v-for="cat in selectedInterests" :key="cat">{{ cat }}</el-tag>
              <span v-if="!selectedInterests.length" class="no-data">暂未设置偏好</span>
            </div>
            <el-button @click="editing = true" size="small" style="margin-top: 8px">修改偏好</el-button>
          </template>
          <template v-else>
            <div class="categories">
              <el-checkbox-group v-model="editInterests">
                <el-checkbox v-for="cat in allCategories" :key="cat" :label="cat">{{ cat }}</el-checkbox>
              </el-checkbox-group>
            </div>
            <div style="margin-top: 8px; display: flex; gap: 8px">
              <el-button type="primary" size="small" @click="saveInterests">保存</el-button>
              <el-button size="small" @click="editing = false; editInterests = [...selectedInterests]">取消</el-button>
            </div>
          </template>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>我的点子</template>
          <el-empty v-if="!myIdeas.length" description="暂无发表" :image-size="60" />
          <div v-else class="idea-list">
            <div v-for="item in myIdeas" :key="item.id" class="idea-item" @click="$router.push(`/ideas/${item.id}`)">
              <div class="idea-main">
                <span class="idea-title">{{ item.title }}</span>
                <div class="idea-meta">
                  <span>{{ item.category }}</span>
                  <span>{{ item.created_at?.slice(0, 10) }}</span>
                  <span>👍 {{ item.likes_count }}</span>
                  <span>💬 {{ item.comments_count }}</span>
                </div>
              </div>
              <el-tag :type="item.status === 'approved' ? 'success' : item.status === 'rejected' ? 'danger' : 'warning'" size="small">
                {{ item.status === 'approved' ? '已通过' : item.status === 'rejected' ? '已拒绝' : '审核中' }}
              </el-tag>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="pwdDialog" title="修改密码" width="400px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-position="top">
        <el-form-item label="原密码" prop="oldPwd">
          <el-input v-model="pwdForm.oldPwd" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="newPwd">
          <el-input v-model="pwdForm.newPwd" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirmPwd">
          <el-input v-model="pwdForm.confirmPwd" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog = false">取消</el-button>
        <el-button type="primary" :loading="pwdLoading" @click="changePassword">确认修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '../api/request';

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
    // shown by interceptor
  } finally {
    pwdLoading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.profile-page { max-width: 1100px; margin: 0 auto; }
.categories { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.no-data { color: #c0c4cc; font-size: 13px; }
.idea-list { display: flex; flex-direction: column; gap: 6px; }
.idea-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; cursor: pointer; }
.idea-item:last-child { border-bottom: none; }
.idea-main { display: flex; flex-direction: column; gap: 4px; flex: 1; }
.idea-title { font-size: 14px; color: #303133; }
.idea-meta { display: flex; gap: 12px; font-size: 12px; color: #909399; }
</style>
