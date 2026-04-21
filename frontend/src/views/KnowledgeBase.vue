<template>
  <div class="kb-container">
    <div class="kb-header">
      <div>
        <button class="back-btn" @click="router.push('/admin')">← 返回管理中心</button>
        <h1 class="kb-title">知识库管理</h1>
      </div>
      <button class="primary-btn" @click="showCreateModal = true">新建知识库</button>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-else-if="kbs.length === 0" class="empty-state">
      <p>暂无知识库</p>
    </div>

    <div v-else class="kb-grid">
      <div v-for="kb in kbs" :key="kb.id" class="kb-card">
        <h3 class="kb-card-title">{{ kb.name }}</h3>
        <p class="kb-card-desc">{{ kb.description || '无描述' }}</p>
        <div class="kb-card-meta">
          <span>创建时间: {{ new Date(kb.created_at).toLocaleDateString() }}</span>
        </div>
        <div class="kb-card-actions">
          <button class="secondary-btn" @click="manageDocs(kb)">管理文档</button>
        </div>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-content">
        <h2>新建知识库</h2>
        <div class="form-group">
          <label>知识库名称</label>
          <input type="text" v-model="newKb.name" placeholder="请输入名称" class="form-input" />
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="newKb.description" placeholder="请输入描述" class="form-input"></textarea>
        </div>
        <div class="modal-actions">
          <button class="secondary-btn" @click="showCreateModal = false">取消</button>
          <button class="primary-btn" @click="createKb" :disabled="!newKb.name.trim()">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'

const router = useRouter()
const kbs = ref<any[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const newKb = ref({ name: '', description: '' })

const fetchKbs = async () => {
  loading.value = true
  try {
    kbs.value = await request.get('/knowledge_bases')
  } catch (error) {
    console.error('Failed to fetch KBs:', error)
  } finally {
    loading.value = false
  }
}

const createKb = async () => {
  try {
    const res = await request.post('/knowledge_bases', newKb.value)
    kbs.value.push(res)
    showCreateModal.value = false
    newKb.value = { name: '', description: '' }
  } catch (error) {
    console.error('Failed to create KB:', error)
    alert('创建失败')
  }
}

const manageDocs = (kb: any) => {
  router.push(`/admin/documents?kb_id=${kb.id}&kb_name=${encodeURIComponent(kb.name)}`)
}

onMounted(() => {
  fetchKbs()
})
</script>

<style scoped>
.kb-container {
  max-width: 1200px;
  margin: 0 auto;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.kb-title {
  font-size: 24px;
  font-weight: 500;
  margin: 0;
}

.back-btn {
  background: none;
  border: none;
  color: #737373;
  cursor: pointer;
  padding: 0;
  font-size: 14px;
  margin-bottom: 8px;
}

.back-btn:hover {
  color: #000000;
}

.primary-btn {
  background: #000000;
  color: #ffffff;
  border: none;
  padding: 10px 24px;
  border-radius: 9999px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.primary-btn:hover:not(:disabled) {
  opacity: 0.8;
}

.primary-btn:disabled {
  background: #e5e5e5;
  color: #a3a3a3;
  cursor: not-allowed;
}

.secondary-btn {
  background: #ffffff;
  color: #262626;
  border: 1px solid #e5e5e5;
  padding: 8px 16px;
  border-radius: 9999px;
  font-size: 14px;
  cursor: pointer;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
}

.kb-card {
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.kb-card-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 500;
}

.kb-card-desc {
  color: #737373;
  font-size: 14px;
  margin: 0 0 16px 0;
  flex-grow: 1;
}

.kb-card-meta {
  font-size: 12px;
  color: #a3a3a3;
  margin-bottom: 16px;
}

.kb-card-actions {
  display: flex;
  justify-content: flex-end;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 64px 0;
  color: #737373;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-content {
  background: #ffffff;
  padding: 32px;
  border-radius: 12px;
  width: 100%;
  max-width: 480px;
}

.modal-content h2 {
  margin: 0 0 24px 0;
  font-weight: 500;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #525252;
}

.form-input {
  width: 100%;
  padding: 10px 16px;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  font-size: 14px;
  box-sizing: border-box;
}

textarea.form-input {
  border-radius: 12px;
  resize: vertical;
  min-height: 80px;
}

.form-input:focus {
  outline: none;
  border-color: #a3a3a3;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}
</style>
