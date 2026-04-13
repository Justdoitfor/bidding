<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import request from '../api/request'

const historyData = ref<any[]>([])
const dialogVisible = ref(false)
const currentMessages = ref<any[]>([])
const selectedSessionTitle = ref('')

// Filters
const searchUser = ref('')

const fetchAllHistory = async () => {
  try {
    const res: any = await request.get('/chat/admin/history')
    historyData.value = res.map((session: any) => ({
      session_id: session.session_id,
      user_id: session.user_id,
      title: session.title,
      created_at: session.created_at,
      messages: session.messages,
      msgCount: session.messages?.length || 0
    }))
  } catch (error) {
    console.error('获取历史记录失败', error)
  }
}

onMounted(() => {
  fetchAllHistory()
})

const filteredData = computed(() => {
  if (!searchUser.value) return historyData.value
  return historyData.value.filter(item => 
    item.user_id.toLowerCase().includes(searchUser.value.toLowerCase())
  )
})

const viewSession = (row: any) => {
  selectedSessionTitle.value = row.title || '会话详情'
  currentMessages.value = row.messages || []
  dialogVisible.value = true
}

const closeDialog = () => {
  dialogVisible.value = false
}

const formatDate = (dateStr: string) => {
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
          <svg class="llama-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/>
          </svg>
          <h1 class="brand-name">招标智脑 - 管理中心</h1>
        </div>
      </div>
    </header>

    <main class="admin-main">
      <div class="admin-container">
        
        <div class="section-header">
          <h2 class="section-title">会话历史记录</h2>
          <button class="action-pill" @click="fetchAllHistory">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            刷新数据
          </button>
        </div>

        <div class="toolbar">
          <div class="search-box">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            <input 
              type="text" 
              class="search-input" 
              v-model="searchUser" 
              placeholder="按用户 ID 过滤..." 
            />
          </div>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>会话 ID</th>
                <th>用户 ID</th>
                <th>提问主题</th>
                <th>创建时间</th>
                <th>消息数</th>
                <th style="text-align: center;">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in filteredData" :key="row.session_id">
                <td class="cell-mono">{{ row.session_id.substring(0, 8) }}...</td>
                <td><span class="tag-pill">{{ row.user_id }}</span></td>
                <td class="cell-primary">{{ row.title }}</td>
                <td class="cell-muted">{{ formatDate(row.created_at) }}</td>
                <td>
                  <span class="count-badge">{{ row.msgCount }}</span>
                </td>
                <td style="text-align: center;">
                  <button class="link-btn" @click="viewSession(row)">查看详情</button>
                </td>
              </tr>
              <tr v-if="filteredData.length === 0">
                <td colspan="6" class="empty-row">暂无相关会话记录</td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    </main>

    <!-- Custom Modal Dialog -->
    <div class="modal-overlay" v-if="dialogVisible" @click.self="closeDialog">
      <div class="modal-content">
        <div class="modal-header">
          <h3 class="modal-title">{{ selectedSessionTitle }}</h3>
          <button class="close-btn" @click="closeDialog">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="dialog-messages">
            <div v-for="(msg, idx) in currentMessages" :key="idx" :class="['dialog-msg', msg.role]">
              <div class="msg-header">
                <span class="role-badge">{{ msg.role === 'assistant' ? 'AI' : '用户' }}</span>
                <span class="time">{{ formatDate(msg.time) }}</span>
              </div>
              <div class="msg-content">{{ msg.content }}</div>
            </div>
            <div v-if="currentMessages.length === 0" class="no-messages">
              暂无消息内容
            </div>
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

/* --- Header --- */
.admin-header {
  padding: 20px 32px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e5e5;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
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

/* --- Main Area --- */
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
  align-items: flex-end;
}

.section-title {
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 30px;
  font-weight: 500;
  margin: 0;
  color: #000000;
  letter-spacing: -0.02em;
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

/* --- Toolbar --- */
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

/* --- Table Styles --- */
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

/* --- Modal Dialog --- */
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
  max-height: 85vh;
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

.modal-body {
  padding: 24px;
  overflow-y: auto;
}

.dialog-messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-msg {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 12px;
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
}

.dialog-msg.user {
  background-color: #fafafa;
}

.msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-badge {
  font-size: 12px;
  font-weight: 600;
  color: #000000;
}

.time {
  font-size: 12px;
  color: #a3a3a3;
}

.msg-content {
  font-size: 14px;
  color: #262626;
  white-space: pre-wrap;
  line-height: 1.5;
}

.no-messages {
  text-align: center;
  color: #a3a3a3;
  padding: 32px;
}
</style>
