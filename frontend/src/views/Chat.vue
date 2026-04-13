<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'
import { ElMessage } from 'element-plus'

const query = ref('')
const messages = ref<{role: string, content: string}[]>([])
const loading = ref(false)
const sessionId = ref<string | null>(null)
const sessions = ref<any[]>([])
const scrollContainer = ref<HTMLElement | null>(null)

const fetchHistory = async () => {
  try {
    const res: any = await request.get('/chat/history?user_id=demo_user')
    sessions.value = res || []
  } catch (error) {
    console.error('获取历史记录失败', error)
  }
}

onMounted(() => {
  fetchHistory()
})

const startNewChat = () => {
  sessionId.value = null
  messages.value = []
}

const selectSession = (session: any) => {
  sessionId.value = session.session_id
  messages.value = session.messages.map((m: any) => ({
    role: m.role,
    content: m.content
  }))
  scrollToBottom()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!query.value.trim() || loading.value) return
  
  const userMsg = query.value
  messages.value.push({ role: 'user', content: userMsg })
  query.value = ''
  loading.value = true
  scrollToBottom()
  
  try {
    const res: any = await request.post('/chat', {
      query: userMsg,
      session_id: sessionId.value,
      domain: 'bidding'
    })
    
    sessionId.value = res.session_id
    messages.value.push({ role: 'assistant', content: res.answer })
    scrollToBottom()
    await fetchHistory() // 刷新左侧会话列表
  } catch (error) {
    ElMessage.error('发送失败，请重试')
    messages.value.pop()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="chat-layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="startNewChat">
          <el-icon><Plus /></el-icon> 新建会话
        </button>
      </div>
      <div class="history-list">
        <div 
          v-for="session in sessions" 
          :key="session.session_id" 
          :class="['history-item', { active: session.session_id === sessionId }]"
          @click="selectSession(session)"
        >
          <el-icon><ChatDotRound /></el-icon>
          <span class="session-title">{{ session.title || '新会话' }}</span>
        </div>
        <div v-if="sessions.length === 0" class="empty-history">
          暂无历史会话
        </div>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="main-content">
      <header class="chat-header">
        <h2>招标智脑 RAG</h2>
      </header>

      <div class="chat-messages" ref="scrollContainer">
        <div v-if="messages.length === 0" class="empty-state">
          <h3>欢迎使用招标智脑</h3>
          <p>请在下方输入您的问题，例如查询企业信息、政策法规或招标数据。</p>
        </div>
        
        <div class="message-wrapper" v-for="(msg, index) in messages" :key="index" :class="msg.role">
          <div class="avatar">{{ msg.role === 'assistant' ? 'AI' : 'U' }}</div>
          <div class="message-bubble">{{ msg.content }}</div>
        </div>
        
        <div v-if="loading" class="message-wrapper assistant">
          <div class="avatar">AI</div>
          <div class="message-bubble loading">正在思考...</div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="input-box">
          <el-input 
            v-model="query" 
            type="textarea"
            :rows="2"
            resize="none"
            placeholder="向招标智脑提问..." 
            @keydown.enter.prevent="sendMessage"
            :disabled="loading"
          />
          <el-button type="primary" :loading="loading" @click="sendMessage" class="send-btn">
            发送
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.chat-layout {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: #f9fafb;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: #1f2937;
  color: #ffffff;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100%;
}

.sidebar-header {
  padding: 16px;
}

.new-chat-btn {
  width: 100%;
  padding: 12px;
  background-color: transparent;
  border: 1px solid #4b5563;
  border-radius: 8px;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  transition: background-color 0.2s;
}

.new-chat-btn:hover {
  background-color: #374151;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #d1d5db;
  transition: all 0.2s;
}

.history-item:hover {
  background-color: #374151;
  color: #ffffff;
}

.history-item.active {
  background-color: #374151;
  color: #ffffff;
}

.session-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-history {
  text-align: center;
  color: #6b7280;
  font-size: 13px;
  margin-top: 20px;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
}

.chat-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e5e7eb;
  background-color: #ffffff;
  color: #111827;
  flex-shrink: 0;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-state {
  margin-top: 10vh;
  text-align: center;
  color: #6b7280;
}

.empty-state h3 {
  font-size: 24px;
  color: #374151;
  margin-bottom: 12px;
}

.message-wrapper {
  width: 100%;
  max-width: 800px;
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  flex-shrink: 0;
}

.assistant .avatar {
  background-color: #10b981;
  color: #ffffff;
}

.user .avatar {
  background-color: #3b82f6;
  color: #ffffff;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.6;
  color: #1f2937;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.assistant .message-bubble {
  background-color: #ffffff;
  border: 1px solid #e5e7eb;
}

.user .message-bubble {
  background-color: #eff6ff;
}

/* Input Area */
.chat-input-area {
  padding: 24px;
  display: flex;
  justify-content: center;
  background: linear-gradient(to bottom, transparent, #f9fafb 20%);
  flex-shrink: 0;
}

.input-box {
  width: 100%;
  max-width: 800px;
  position: relative;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 8px;
}

.input-box :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  padding-right: 80px;
  font-size: 15px;
}

.input-box :deep(.el-textarea__inner:focus) {
  box-shadow: none;
}

.send-btn {
  position: absolute;
  right: 16px;
  bottom: 16px;
}
</style>
