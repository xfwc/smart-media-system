<template>
  <div class="idea-create">
    <h2>发布新点子</h2>
    <el-card style="max-width: 700px; margin: 0 auto">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="给点子起个吸引人的标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category" placeholder="选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="6" placeholder="详细描述你的创意..." maxlength="5000" show-word-limit />
        </el-form-item>
        <el-form-item label="标签">
          <el-tag v-for="tag in form.tags" :key="tag" closable @close="removeTag(tag)" style="margin-right: 8px">{{ tag }}</el-tag>
          <el-input v-if="tagInputVisible" ref="tagInputRef" v-model="tagInputValue" size="small" @blur="addTag" @keyup.enter="addTag" style="width: 100px" />
          <el-button v-else size="small" @click="showTagInput">+ 添加标签</el-button>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="form.is_anonymous">匿名发布</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="submit" style="width: 100%">发布</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import request from '../api/request';

const router = useRouter();
const loading = ref(false);
const categories = ['时政', '财经', '科技', '娱乐', '体育', '美食', '教育', '其他'];
const form = reactive({ title: '', category: '', content: '', tags: [], is_anonymous: false });
const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
};

const tagInputVisible = ref(false);
const tagInputValue = ref('');
const tagInputRef = ref(null);

function showTagInput() { tagInputVisible.value = true; nextTick(() => tagInputRef.value?.focus()); }
function addTag() {
  if (tagInputValue.value && !form.tags.includes(tagInputValue.value)) form.tags.push(tagInputValue.value);
  tagInputVisible.value = false;
  tagInputValue.value = '';
}
function removeTag(tag) { form.tags = form.tags.filter(t => t !== tag); }

async function submit() {
  loading.value = true;
  try {
    await request.post('/ideas', form);
    ElMessage.success('发布成功，等待审核');
    router.push('/ideas');
  } finally { loading.value = false; }
}
</script>
