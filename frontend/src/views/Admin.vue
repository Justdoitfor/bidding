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
      <h1>招标智脑 - 会话管理后台</h1>
    </header>

    <main class="admin-main">
      <div class="admin-container">
        <div class="toolbar">
          <el-input 
            v-model="searchUser" 
            placeholder="按用户ID过滤..." 
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="fetchAllHistory">
            <el-icon><Refresh /></el-icon> 刷新数据
          </el-button>
        </div>

        <el-table :data="filteredData" border style="width: 100%" class="history-table">
          <el-table-column prop="session_id" label="会话 ID" width="300">
            <template #default="{ row }">
              <span class="mono-text">{{ row.session_id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="user_id" label="用户 ID" width="180">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ row.user_id }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="提问主题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="msgCount" label="消息数" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="success" round>{{ row.msgCount }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewSession(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </main>

    <!-- Session Detail Dialog -->
    <el-dialog v-model="dialogVisible" :title="selectedSessionTitle" width="800px" destroy-on-close>
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
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background-color: #f3f4f6;
  overflow: hidden;
}

.admin-header {
  background-color: #ffffff;
  padding: 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.admin-header h1 {
  font-size: 20px;
  color: #111827;
  margin: 0;
  font-weight: 600;
}

.admin-main {
  flex: 1;
  padding: 32px;
  display: flex;
  justify-content: center;
  overflow-y: auto;
}

.admin-container {
  width: 100%;
  max-width: 1400px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: fit-content;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-input {
  width: 300px;
}

.mono-text {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #6b7280;
  font-size: 13px;
}

/* Dialog Styles */
.dialog-messages {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 8px;
}

.dialog-msg {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  border-radius: 8px;
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
}

.dialog-msg.user {
  border-left: 4px solid #3b82f6;
}

.dialog-msg.assistant {
  border-left: 4px solid #10b981;
}

.msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.role-badge {
  font-size: 12px;
  font-weight: bold;
  color: #374151;
}

.time {
  font-size: 12px;
  color: #9ca3af;
}

.msg-content {
  font-size: 14px;
  color: #1f2937;
  white-space: pre-wrap;
  line-height: 1.5;
}

.no-messages {
  text-align: center;
  color: #9ca3af;
  padding: 32px;
}
</style>
