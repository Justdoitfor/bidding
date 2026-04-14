<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import request from '../api/request'
import BrandMark from '../components/BrandMark.vue'

const currentUser = ref(JSON.parse(localStorage.getItem('current_user') || '{}'))

// Tabs
const activeTab = ref('sessions') // 'sessions' | 'users'

// Sessions Data
const historyData = ref<any[]>([])
const dialogVisible = ref(false)
const currentMessages = ref<any[]>([])
const selectedSessionTitle = ref('')
const searchSession = ref('')

// Users Data
const usersData = ref<any[]>([])
const searchUser = ref('')

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
  localStorage.removeItem('access_token')
  localStorage.removeItem('current_user')
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
          </div>
          <button class="action-pill" @click="activeTab === 'sessions' ? fetchAllHistory() : fetchUsers()">
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
                </tr>
                <tr v-if="filteredUsers.length === 0">
                  <td colspan="4" class="empty-row">暂无用户记录</td>
                </tr>
              </tbody>
            </table>
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
              <div class="bubble-text">{{ msg.content }}</div>
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
</style>
