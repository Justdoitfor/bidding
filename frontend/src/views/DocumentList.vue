<template>
  <div class="doc-container">
    <div class="doc-header">
      <div>
        <button class="back-btn" @click="router.push('/admin/kb')">← 返回知识库</button>
        <h1 class="doc-title">{{ kbName }} - 文档管理</h1>
      </div>
      <div class="upload-section">
        <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv,.xlsx,.json" style="display: none" />
        <button class="primary-btn" @click="() => fileInput?.click()" :disabled="uploading">
          {{ uploading ? '上传中...' : '上传新文档' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>

    <div v-else-if="documents.length === 0" class="empty-state">
      <p>暂无文档，请上传您的业务数据文件 (.csv, .xlsx, .json)</p>
    </div>

    <div v-else class="doc-table-container">
      <table class="doc-table">
        <thead>
          <tr>
            <th>文件名</th>
            <th>状态</th>
            <th>上传时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="doc in documents" :key="doc.id">
            <td>{{ doc.filename }}</td>
            <td>
              <span :class="['status-badge', doc.status]">
                {{ getStatusText(doc.status) }}
              </span>
            </td>
            <td>{{ new Date(doc.created_at).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import request from '../api/request'

const route = useRoute()
const router = useRouter()
const fileInput = ref<HTMLInputElement | null>(null)

const kbId = computed(() => route.query.kb_id as str || 'global')
const kbName = computed(() => route.query.kb_name as str || '全局知识库')

const documents = ref<any[]>([])
const loading = ref(true)
const uploading = ref(false)

const fetchDocuments = async () => {
  loading.value = true
  try {
    documents.value = await request.get(`/documents?kb_id=${kbId.value}`)
  } catch (error) {
    console.error('Failed to fetch documents:', error)
  } finally {
    loading.value = false
  }
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  
  const file = target.files[0]
  const formData = new FormData()
  formData.append('file', file)
  if (kbId.value !== 'global') {
    formData.append('kb_id', kbId.value)
  }
  
  uploading.value = true
  try {
    const token = localStorage.getItem('admin_access_token') || localStorage.getItem('access_token')
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    if (!response.ok) throw new Error('Upload failed')
    
    alert('文件上传成功，正在后台解析入库')
    await fetchDocuments()
  } catch (error) {
    console.error('Upload error:', error)
    alert('上传失败，请检查文件格式或网络')
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

const getStatusText = (status: str) => {
  const map: Record<string, string> = {
    'uploaded': '已上传',
    'processing': '处理中',
    'success': '入库成功',
    'failed': '解析失败'
  }
  return map[status] || status
}

onMounted(() => {
  fetchDocuments()
  // Poll for status updates
  setInterval(() => {
    if (documents.value.some(d => d.status === 'processing' || d.status === 'uploaded')) {
      fetchDocuments()
    }
  }, 5000)
})
</script>

<style scoped>
.doc-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
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

.doc-title {
  font-size: 24px;
  font-weight: 500;
  margin: 0;
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

.doc-table-container {
  background: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
}

.doc-table {
  width: 100%;
  border-collapse: collapse;
}

.doc-table th, .doc-table td {
  padding: 16px 24px;
  text-align: left;
  border-bottom: 1px solid #e5e5e5;
}

.doc-table th {
  background: #fafafa;
  font-weight: 500;
  color: #525252;
  font-size: 14px;
}

.doc-table tr:last-child td {
  border-bottom: none;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.status-badge.processing {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.status-badge.failed {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.status-badge.uploaded {
  background: #faf5ff;
  color: #4338ca;
  border: 1px solid #e9d5ff;
}

.empty-state, .loading-state {
  text-align: center;
  padding: 64px 0;
  color: #737373;
}
</style>
