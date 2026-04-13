<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'
import BrandMark from '../components/BrandMark.vue'

const query = ref('')
const messages = ref<{role: string, content: string}[]>([])
const loading = ref(false)
const sessionId = ref<string | null>(null)
const sessions = ref<any[]>([])
const scrollContainer = ref<HTMLElement | null>(null)

const fetchHistory = async () => {
  try {
    const res: any = await request.get('/chat/history')
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

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('current_user')
  window.location.href = '/login'
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
        <div class="logo-area">
          <BrandMark :size="24" class="llama-icon" />
          <h1 class="brand-name">招投标信息智能问答平台</h1>
        </div>
        <button class="new-chat-btn" @click="startNewChat">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          新建会话
        </button>
      </div>
      <div class="history-list">
        <div class="history-label">历史记录</div>
        <div 
          v-for="session in sessions" 
          :key="session.session_id" 
          :class="['history-item', { active: session.session_id === sessionId }]"
          @click="selectSession(session)"
        >
          <span class="session-title">{{ session.title || '新会话' }}</span>
        </div>
        <div v-if="sessions.length === 0" class="empty-history">
          暂无历史会话
        </div>
      </div>
      <div class="sidebar-footer">
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <main class="main-content">
      <div class="chat-messages" ref="scrollContainer">
        <!-- Empty State -->
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-llama">
            <BrandMark :size="64" />
          </div>
          <h2 class="hero-title">开始使用招投标信息智能问答平台</h2>
          <p class="hero-subtitle">您可以提问关于企业信息、政策法规、招标数据及商品价格等任何问题。</p>
          
          <div class="suggestion-grid">
            <button class="suggestion-pill" @click="query = '查询北京科技有限公司的工商信息'; sendMessage()">
              查询企业信息
            </button>
            <button class="suggestion-pill" @click="query = '最近有哪些高性能服务器的招标项目？'; sendMessage()">
              查找招标项目
            </button>
            <button class="suggestion-pill" @click="query = '中华人民共和国招标投标法的核心内容是什么？'; sendMessage()">
              检索政策法规
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div v-else class="message-wrapper-container">
          <div v-for="(msg, index) in messages" :key="index" :class="['message-wrapper', msg.role]">
            <div class="message-avatar" v-if="msg.role === 'assistant'">
              <BrandMark :size="24" />
            </div>
            <div class="message-content">
              {{ msg.content }}
            </div>
          </div>
          <div v-if="loading" class="message-wrapper assistant">
            <div class="message-avatar">
              <BrandMark :size="24" />
            </div>
            <div class="message-content loading-indicator">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="chat-input-area">
        <div class="input-container">
          <input 
            type="text" 
            class="chat-input" 
            v-model="query" 
            placeholder="请输入问题…" 
            @keyup.enter="sendMessage"
            :disabled="loading"
          />
          <button class="send-btn" @click="sendMessage" :disabled="loading || !query.trim()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
        <div class="input-footer">系统可能会产生误差，请验证重要信息。</div>
      </div>
    </main>
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'SF Pro Rounded';
  src: local('SF Pro Rounded'), local('-apple-system');
  font-weight: 400 600;
}

.chat-layout {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
  background-color: #ffffff;
  color: #000000;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* --- Sidebar --- */
.sidebar {
  width: 280px;
  background-color: #fafafa;
  border-right: 1px solid #e5e5e5;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100%;
}

.sidebar-header {
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.llama-icon {
  width: 24px;
  height: 24px;
  color: #000000;
}

.brand-name {
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  letter-spacing: -0.02em;
}

.new-chat-btn {
  width: 100%;
  background-color: #ffffff;
  color: #262626;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 10px 24px;
  font-size: 16px;
  font-weight: 400;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-family: inherit;
}

.new-chat-btn svg {
  width: 16px;
  height: 16px;
}

.new-chat-btn:hover {
  background-color: #e5e5e5;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-footer {
  padding: 16px 20px 20px;
  border-top: 1px solid #e5e5e5;
}

.logout-btn {
  width: 100%;
  background-color: #ffffff;
  color: #404040;
  border: 1px solid #d4d4d4;
  border-radius: 9999px;
  padding: 10px 24px;
  font-size: 16px;
  cursor: pointer;
  font-family: inherit;
}

.logout-btn:hover {
  background-color: #e5e5e5;
  color: #000000;
  border-color: #e5e5e5;
}

.history-label {
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 500;
  color: #737373;
  margin-top: 8px;
}

.history-item {
  padding: 10px 16px;
  border-radius: 9999px;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #525252;
}

.history-item:hover {
  background-color: #e5e5e5;
  color: #000000;
}

.history-item.active {
  background-color: #e5e5e5;
  color: #000000;
  font-weight: 500;
}

.session-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.empty-history {
  padding: 12px;
  color: #a3a3a3;
  font-size: 14px;
}

/* --- Main Content --- */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
  background-color: #ffffff;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20px;
  scrollbar-width: none;
}
.chat-messages::-webkit-scrollbar {
  display: none;
}

.message-wrapper-container {
  width: 100%;
  max-width: 800px;
  padding: 40px 0 120px 0;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* --- Empty State --- */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 10vh;
  width: 100%;
  max-width: 800px;
}

.empty-llama {
  margin-bottom: 24px;
}

.empty-llama svg {
  width: 64px;
  height: 64px;
  color: #000000;
  stroke-width: 1px;
}

.hero-title {
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 36px;
  font-weight: 500;
  margin: 0 0 16px 0;
  color: #000000;
  letter-spacing: -0.02em;
  text-align: center;
}

.hero-subtitle {
  font-size: 18px;
  color: #737373;
  margin: 0 0 48px 0;
  text-align: center;
  font-weight: 400;
}

.suggestion-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-pill {
  background-color: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 10px 24px;
  font-size: 14px;
  color: #525252;
  cursor: pointer;
  font-family: inherit;
}

.suggestion-pill:hover {
  background-color: #e5e5e5;
  color: #000000;
}

/* --- Messages --- */
.message-wrapper {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  width: 100%;
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-avatar svg {
  width: 24px;
  height: 24px;
  color: #000000;
}

.message-content {
  font-size: 16px;
  line-height: 1.5;
  color: #000000;
  padding: 12px 16px;
  max-width: 80%;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.user .message-content {
  background-color: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 20px 20px 4px 20px;
}

.assistant .message-content {
  background-color: #ffffff;
  padding: 8px 0;
}

/* --- Input Area --- */
.chat-input-area {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 20%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.input-container {
  position: relative;
  width: 100%;
  max-width: 760px;
  display: flex;
  align-items: center;
}

.chat-input {
  width: 100%;
  background-color: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 16px 56px 16px 24px;
  font-size: 16px;
  color: #000000;
  font-family: inherit;
  outline: none;
}

.chat-input:focus {
  border-color: #d4d4d4;
  background-color: #ffffff;
}

.chat-input::placeholder {
  color: #a3a3a3;
}

.send-btn {
  position: absolute;
  right: 12px;
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  background-color: #000000;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 0;
}

.send-btn:disabled {
  background-color: #e5e5e5;
  cursor: not-allowed;
}

.send-btn svg {
  width: 16px;
  height: 16px;
  color: #ffffff;
}

.send-btn:disabled svg {
  color: #a3a3a3;
}

.input-footer {
  margin-top: 12px;
  font-size: 12px;
  color: #a3a3a3;
  text-align: center;
}

/* Loading animation */
.loading-indicator span {
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
  font-size: 24px;
  line-height: 0;
}
.loading-indicator span:nth-child(1) { animation-delay: -0.32s; }
.loading-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
