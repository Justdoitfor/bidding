<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import request from '../api/request'
import BrandMark from '../components/BrandMark.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const currentUser = ref(JSON.parse(localStorage.getItem('admin_current_user') || '{}'))

// Configure marked to use breaks for newlines
marked.setOptions({
  breaks: true,
  gfm: true
})

const renderMarkdown = (text: string) => {
  if (!text) return ''
  const rawHtml = marked(text) as string
  return DOMPurify.sanitize(rawHtml)
}

// Tabs
const activeTab = ref('sessions') // 'sessions' | 'users' | 'data'

// Sessions Data
const historyData = ref<any[]>([])
const dialogVisible = ref(false)
const currentMessages = ref<any[]>([])
const selectedSessionTitle = ref('')
const searchSession = ref('')

// Users Data
const usersData = ref<any[]>([])
const searchUser = ref('')

// Data Upload
const uploadStatus = ref('')
const uploadMessage = ref('')
const selectedTableType = ref('company')
const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  
  const file = target.files[0]
  uploadStatus.value = 'uploading'
  uploadMessage.value = `正在上传 ${file.name}...`
  
  const formData = new FormData()
  formData.append('file', file)
  formData.append('table_type', selectedTableType.value)
  
  try {
    const res: any = await request.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    uploadStatus.value = 'success'
    uploadMessage.value = res.message || '文件上传成功，正在后台处理中'
  } catch (error: any) {
    uploadStatus.value = 'error'
    uploadMessage.value = error.response?.data?.message || error.response?.data?.detail || '文件上传失败'
    console.error('上传失败', error)
  } finally {
    // Reset file input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  if (!event.dataTransfer?.files || event.dataTransfer.files.length === 0) return
  
  // Assign files to the hidden input and trigger upload
  if (fileInput.value) {
    fileInput.value.files = event.dataTransfer.files
    const changeEvent = new Event('change', { bubbles: true })
    fileInput.value.dispatchEvent(changeEvent)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
}

const fetchAllHistory = async () => {
  try {
    const res: any = await request.get('/chat/admin/history')
    historyData.value = (res || []).map((session: any) => ({
      session_id: session.session_id || '',
      user_id: session.user_id || '',
      username: session.username || '',
      title: session.title || '新会话',
      created_at: session.created_at || '',
      messages: session.messages || [],
      msgCount: session.messages?.length || 0
    }))
  } catch (error) {
    console.error('获取历史记录失败', error)
  }
}

const fetchUsers = async () => {
  try {
    const res: any = await request.get('/users')
    usersData.value = res || []
  } catch (error) {
    console.error('获取用户列表失败', error)
  }
}

const toggleUserStatus = async (user: any) => {
  if (!confirm(`确定要${user.is_active ? '禁用' : '启用'}用户 ${user.username} 吗？`)) return
  try {
    await request.patch(`/users/${user.id}`, { is_active: !user.is_active })
    fetchUsers()
  } catch (error) {
    console.error('更新用户状态失败', error)
  }
}

const deleteUser = async (user: any) => {
  if (!confirm(`确定要永久删除用户 ${user.username} 吗？此操作将同时删除其所有会话记录。`)) return
  try {
    await request.delete(`/users/${user.id}`)
    fetchUsers()
    fetchAllHistory()
  } catch (error) {
    console.error('删除用户失败', error)
  }
}

onMounted(() => {
  fetchAllHistory()
  fetchUsers()
})

const filteredSessions = computed(() => {
  if (!searchSession.value) return historyData.value
  const q = searchSession.value.toLowerCase()
  return historyData.value.filter(item => {
    const key = (item.username || item.user_id || '').toLowerCase()
    return key.includes(q)
  })
})

const filteredUsers = computed(() => {
  if (!searchUser.value) return usersData.value
  const q = searchUser.value.toLowerCase()
  return usersData.value.filter(item => {
    const key = (item.username || item.id || '').toLowerCase()
    return key.includes(q)
  })
})

const viewSession = (row: any) => {
  selectedSessionTitle.value = row.title || '会话详情'
  currentMessages.value = row.messages || []
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
}

const logout = () => {
  localStorage.removeItem('admin_access_token')
  localStorage.removeItem('admin_current_user')
  window.location.href = '/admin/login'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { 
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}
</script>

<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="header-content">
        <div class="logo-area">
          <BrandMark :size="28" class="llama-icon" />
          <h1 class="brand-name">招投标信息智能问答平台 - 管理中心</h1>
        </div>
        <div class="user-area">
          <router-link to="/admin/kb" class="action-pill" style="margin-right: 12px; text-decoration: none; color: inherit;">知识库管理</router-link>
          <span class="username-badge">{{ currentUser.username || 'Admin' }}</span>
          <button class="action-pill" @click="logout">退出登录</button>
        </div>
      </div>
    </header>

    <main class="admin-main">
      <div class="admin-container">
        
        <div class="section-header">
          <div class="tabs">
            <button :class="['tab-btn', { active: activeTab === 'sessions' }]" @click="activeTab = 'sessions'">会话记录</button>
            <button :class="['tab-btn', { active: activeTab === 'users' }]" @click="activeTab = 'users'">用户管理</button>
            <button :class="['tab-btn', { active: activeTab === 'data' }]" @click="activeTab = 'data'">数据入库</button>
          </div>
          <button v-if="activeTab !== 'data'" class="action-pill" @click="activeTab === 'sessions' ? fetchAllHistory() : fetchUsers()">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            刷新数据
          </button>
        </div>

        <!-- Sessions Tab -->
        <div v-if="activeTab === 'sessions'" class="tab-content">
          <div class="toolbar">
            <div class="search-box">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
              <input type="text" class="search-input" v-model="searchSession" placeholder="按用户名/ID过滤..." />
            </div>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>会话 ID</th>
                  <th>用户</th>
                  <th>提问主题</th>
                  <th>创建时间</th>
                  <th>消息数</th>
                  <th style="text-align: center;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in filteredSessions" :key="row.session_id">
                  <td class="cell-mono">{{ row.session_id.substring(0, 8) }}...</td>
                  <td><span class="tag-pill">{{ row.username || row.user_id.substring(0,8) }}</span></td>
                  <td class="cell-primary">{{ row.title }}</td>
                  <td class="cell-muted">{{ formatDate(row.created_at) }}</td>
                  <td><span class="count-badge">{{ row.msgCount }}</span></td>
                  <td style="text-align: center;">
                    <button class="link-btn" @click="viewSession(row)">查看详情</button>
                  </td>
                </tr>
                <tr v-if="filteredSessions.length === 0">
                  <td colspan="6" class="empty-row">暂无相关会话记录</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Users Tab -->
        <div v-if="activeTab === 'users'" class="tab-content">
          <div class="toolbar">
            <div class="search-box">
              <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
              <input type="text" class="search-input" v-model="searchUser" placeholder="按用户名/ID过滤..." />
            </div>
          </div>
          <div class="table-container">
            <table class="data-table">
              <thead>
                <tr>
                  <th>用户 ID</th>
                  <th>用户名</th>
                  <th>角色</th>
                  <th>状态</th>
                  <th style="text-align: center;">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in filteredUsers" :key="user.id">
                  <td class="cell-mono">{{ user.id.substring(0, 8) }}...</td>
                  <td class="cell-primary">{{ user.username }}</td>
                  <td>
                    <span :class="['role-tag', user.is_admin ? 'admin' : 'user']">
                      {{ user.is_admin ? '管理员' : '普通用户' }}
                    </span>
                  </td>
                  <td>
                    <span :class="['status-dot', user.is_active ? 'active' : 'inactive']"></span>
                    {{ user.is_active ? '正常' : '禁用' }}
                  </td>
                  <td style="text-align: center;">
                    <div class="action-links" v-if="user.id !== currentUser.id">
                      <button class="link-btn" @click="toggleUserStatus(user)">{{ user.is_active ? '禁用' : '启用' }}</button>
                      <button class="link-btn danger" @click="deleteUser(user)">删除</button>
                    </div>
                    <span class="cell-muted" v-else>当前账号</span>
                  </td>
                </tr>
                <tr v-if="filteredUsers.length === 0">
                  <td colspan="5" class="empty-row">暂无用户记录</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Data Ingestion Tab -->
        <div v-if="activeTab === 'data'" class="tab-content">
          <div class="data-ingestion-panel">
            <div class="panel-header">
              <h3>真实数据导入</h3>
              <p class="panel-desc">通过下方组件，将企业、产品、法规等结构化数据导入至向量库（Milvus）和关系库（MySQL）。</p>
            </div>
            
            <div class="upload-section">
              <div class="form-group">
                <label>选择要导入的数据类型：</label>
                <select v-model="selectedTableType" class="type-select">
                  <option value="company">企业信息 (Company)</option>
                  <option value="law">政策法规 (Law)</option>
                  <option value="product">产品数据 (Product)</option>
                  <option value="zhaobiao">招标公告 (Zhaobiao)</option>
                  <option value="zhongbiao">中标公示 (Zhongbiao)</option>
                </select>
              </div>

              <div class="upload-zone" @drop="handleDrop" @dragover="handleDragOver" @click="triggerFileInput">
                <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#a3a3a3" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <span class="upload-text">拖拽数据文件至此处，或 <button class="link-btn">点击上传</button></span>
                <span class="upload-hint">支持 .csv, .json, .xlsx 格式（建议单文件不超过 50MB）</span>
                <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv,.xlsx,.json" style="display: none;" />
              </div>

              <div v-if="uploadStatus" :class="['upload-status-alert', uploadStatus]">
                <span class="status-icon" v-if="uploadStatus === 'uploading'">⏳</span>
                <span class="status-icon" v-if="uploadStatus === 'success'">✅</span>
                <span class="status-icon" v-if="uploadStatus === 'error'">❌</span>
                {{ uploadMessage }}
              </div>
            </div>

            <div class="manual-instruction">
              <div class="instruction-header">
                <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
                <h4>大批量数据终端入库指引</h4>
              </div>
              <div class="code-block">
                <div class="code-line"><span class="comment"># 1. 宿主机设置外部数据目录环境变量并重启容器 (例如真实数据在 E:\data)</span></div>
                <div class="code-line"><span class="command">$env:EXTERNAL_DATA_DIR="E:\data"</span></div>
                <div class="code-line"><span class="command">docker-compose -f docker-compose.dev.yml up -d</span></div>
                <div class="code-line"><span class="comment"># 2. 进入后端容器</span></div>
                <div class="code-line"><span class="command">docker-compose -f docker-compose.dev.yml exec backend bash</span></div>
                <div class="code-line"><span class="comment"># 3. 一键导入外部目录下的所有数据（确保文件名包含类型关键字）</span></div>
                <div class="code-line"><span class="command">python scripts/import_real_data.py --dir /data</span></div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- Custom Modal Dialog for Chat Bubbles -->
    <div class="modal-overlay" v-if="dialogVisible" @click.self="closeDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">{{ selectedSessionTitle }}</h3>
          <button class="close-btn" @click="closeDialog">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        <div class="modal-body chat-bubbles-container">
          <div v-for="(msg, idx) in currentMessages" :key="idx" :class="['bubble-wrapper', msg.role]">
            <div class="bubble-avatar" v-if="msg.role === 'assistant'">
              <BrandMark :size="24" />
            </div>
            <div class="bubble-content">
              <div class="bubble-meta" v-if="msg.role === 'assistant'">
                <span class="role-name">AI助手</span>
                <span class="msg-time">{{ formatDate(msg.time) }}</span>
              </div>
              <div class="bubble-meta" v-else>
                <span class="msg-time">{{ formatDate(msg.time) }}</span>
                <span class="role-name">用户</span>
              </div>
              <div class="bubble-text" v-if="msg.role === 'user'">{{ msg.content }}</div>
              <div class="bubble-text markdown-body" v-else v-html="renderMarkdown(msg.content)"></div>
            </div>
            <div class="bubble-avatar" v-if="msg.role === 'user'">
              <div class="user-avatar-placeholder">U</div>
            </div>
          </div>
          <div v-if="currentMessages.length === 0" class="no-messages">
            暂无消息内容
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'SF Pro Rounded';
  src: local('SF Pro Rounded'), local('-apple-system');
  font-weight: 400 600;
}

.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  background-color: #fafafa;
  color: #000000;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.admin-header {
  padding: 20px 32px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e5e5;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1280px;
  margin: 0 auto;
  width: 100%;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.llama-icon {
  width: 28px;
  height: 28px;
  color: #000000;
}

.brand-name {
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 20px;
  font-weight: 500;
  margin: 0;
  letter-spacing: -0.02em;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username-badge {
  font-size: 14px;
  font-weight: 500;
  color: #525252;
  background-color: #f5f5f5;
  padding: 6px 12px;
  border-radius: 9999px;
  border: 1px solid #e5e5e5;
}

.admin-main {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 48px 32px;
  overflow-y: auto;
}

.admin-container {
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 16px;
}

.tabs {
  display: flex;
  gap: 24px;
}

.tab-btn {
  background: none;
  border: none;
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 24px;
  font-weight: 500;
  color: #a3a3a3;
  cursor: pointer;
  padding: 0;
  padding-bottom: 4px;
  position: relative;
}

.tab-btn.active {
  color: #000000;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -17px;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: #000000;
}

.action-pill {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: inherit;
}

.action-pill:hover {
  background-color: #f5f5f5;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  align-items: center;
}

.search-box {
  position: relative;
  width: 300px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #737373;
}

.search-input {
  width: 100%;
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 10px 16px 10px 40px;
  font-size: 14px;
  color: #000000;
  font-family: inherit;
  outline: none;
}

.search-input:focus {
  border-color: #d4d4d4;
}

.search-input::placeholder {
  color: #a3a3a3;
}

.table-container {
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  background-color: #fafafa;
  color: #737373;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e5e5;
}

.data-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #e5e5e5;
  font-size: 14px;
  color: #262626;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr:hover {
  background-color: #fafafa;
}

.cell-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #737373;
}

.cell-primary {
  font-weight: 500;
  color: #000000;
}

.cell-muted {
  color: #a3a3a3;
}

.tag-pill {
  display: inline-block;
  padding: 4px 12px;
  background-color: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  font-size: 12px;
  color: #525252;
}

.count-badge {
  display: inline-block;
  padding: 2px 10px;
  background-color: #000000;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  color: #ffffff;
}

.role-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}
.role-tag.admin {
  background-color: #000000;
  color: #ffffff;
}
.role-tag.user {
  background-color: #f5f5f5;
  color: #525252;
  border: 1px solid #e5e5e5;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}
.status-dot.active { background-color: #10b981; }
.status-dot.inactive { background-color: #ef4444; }

.link-btn {
  background: none;
  border: none;
  color: #000000;
  text-decoration: underline;
  cursor: pointer;
  font-size: 14px;
  font-family: inherit;
}

.link-btn:hover {
  color: #525252;
}

.empty-row {
  text-align: center;
  padding: 48px !important;
  color: #a3a3a3 !important;
}

.action-links {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.link-btn.danger {
  color: #ef4444;
}

.link-btn.danger:hover {
  color: #b91c1c;
}

/* --- Data Ingestion Panel --- */
.data-ingestion-panel {
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.upload-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.type-select {
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #e5e5e5;
  background-color: #ffffff;
  font-size: 14px;
  color: #000000;
  outline: none;
}

.type-select:focus {
  border-color: #a3a3a3;
}

.upload-status-alert {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.upload-status-alert.uploading {
  background-color: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
}

.upload-status-alert.success {
  background-color: #f0fdf4;
  color: #15803d;
  border: 1px solid #bbf7d0;
}

.upload-status-alert.error {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.panel-header h3 {
  margin: 0 0 8px 0;
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 20px;
  font-weight: 500;
  color: #000000;
}

.panel-desc {
  margin: 0;
  font-size: 14px;
  color: #737373;
  line-height: 1.5;
}

.upload-zone {
  border: 2px dashed #e5e5e5;
  border-radius: 12px;
  padding: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background-color: #fafafa;
  transition: all 0.2s ease;
}

.upload-zone:hover {
  border-color: #a3a3a3;
  background-color: #f5f5f5;
}

.upload-text {
  font-size: 16px;
  color: #262626;
}

.upload-text b {
  font-weight: 500;
}

.upload-hint {
  font-size: 14px;
  color: #a3a3a3;
}

.manual-instruction {
  background-color: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 24px;
}

.instruction-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  color: #000000;
}

.instruction-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.code-block {
  background-color: #000000;
  border-radius: 8px;
  padding: 16px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #e5e5e5;
  overflow-x: auto;
}

.code-line .comment {
  color: #737373;
}

.code-line .command {
  color: #ffffff;
}

/* --- Modal Dialog with Chat Bubbles --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #ffffff;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid #e5e5e5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 20px;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #737373;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #000000;
}

.chat-bubbles-container {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: #fafafa;
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}

.bubble-wrapper {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  width: 100%;
}

.bubble-wrapper.user {
  justify-content: flex-end;
}

.bubble-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.bubble-avatar svg {
  width: 24px;
  height: 24px;
  color: #000000;
}

.user-avatar-placeholder {
  width: 32px;
  height: 32px;
  background-color: #e5e5e5;
  color: #525252;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.bubble-content {
  display: flex;
  flex-direction: column;
  max-width: 75%;
}

.bubble-wrapper.user .bubble-content {
  align-items: flex-end;
}

.bubble-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 4px;
}

.role-name {
  font-size: 12px;
  font-weight: 600;
  color: #525252;
}

.msg-time {
  font-size: 12px;
  color: #a3a3a3;
}

.bubble-text {
  font-size: 14px;
  color: #262626;
  padding: 12px 16px;
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.5;
}

.bubble-wrapper.assistant .bubble-text {
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 4px 16px 16px 16px;
}

.bubble-wrapper.user .bubble-text {
  background-color: #000000;
  color: #ffffff;
  border-radius: 16px 4px 16px 16px;
}

.no-messages {
  text-align: center;
  color: #a3a3a3;
  padding: 32px;
}

/* --- Markdown Styles --- */
.markdown-body {
  font-size: 15px;
  line-height: 1.2;
  color: #24292f;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin-top: 6px;
  margin-bottom: 4px;
  font-weight: 600;
  line-height: 1.15;
}

.markdown-body :deep(h1) { font-size: 1.5em; }
.markdown-body :deep(h2) { font-size: 1.3em; padding-bottom: 0.1em; border-bottom: 1px solid #hsla(210,18%,87%,1); }
.markdown-body :deep(h3) { font-size: 1.1em; }

.markdown-body :deep(p) {
  margin-top: 0;
  margin-bottom: 4px;
}

.markdown-body :deep(a) {
  color: #0969da;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin-top: 0;
  margin-bottom: 4px;
  padding-left: 1.5em;
}

.markdown-body :deep(li) {
  margin-top: 0.1em;
}

.markdown-body :deep(code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(175,184,193,0.2);
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
}

.markdown-body :deep(pre) {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body :deep(pre code) {
  padding: 0;
  margin: 0;
  font-size: 100%;
  word-break: normal;
  white-space: pre;
  background: transparent;
  border: 0;
}

.markdown-body :deep(blockquote) {
  margin: 0 0 16px 0;
  padding: 0 1em;
  color: #57606a;
  border-left: 0.25em solid #d0d7de;
}

.markdown-body :deep(table) {
  border-spacing: 0;
  border-collapse: collapse;
  margin-top: 0;
  margin-bottom: 16px;
  width: 100%;
  overflow: auto;
}

.markdown-body :deep(table th),
.markdown-body :deep(table td) {
  padding: 6px 13px;
  border: 1px solid #d0d7de;
}

.markdown-body :deep(table tr:nth-child(2n)) {
  background-color: #f6f8fa;
}
</style>
