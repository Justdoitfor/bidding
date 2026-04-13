<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'
import { useRouter } from 'vue-router'

const router = useRouter()
const query = ref('')
const messages = ref<{role: string, content: string}[]>([])
const loading = ref(false)
const sessionId = ref<string | null>(null)
const scrollContainer = ref<HTMLElement | null>(null)

const fetchHistory = async () => {
  try {
    const res: any = await request.get('/chat/history?user_id=demo_user')
    if (res && res.length > 0) {
      sessionId.value = res[0].session_id
      messages.value = res[0].messages.map((m: any) => ({
        role: m.role,
        content: m.content
      }))
      scrollToBottom()
    }
  } catch (error) {
    console.error('Failed to load history', error)
  }
}

onMounted(() => {
  fetchHistory()
})

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
      session_id: sessionId.value
    })
    
    sessionId.value = res.session_id
    messages.value.push({ role: 'assistant', content: res.answer })
    scrollToBottom()
  } catch (error) {
    messages.value.pop() // remove user message on fail
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="chat-layout">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="logo-area">
          <svg class="llama-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/>
          </svg>
          <h1 class="brand-name">招标智脑</h1>
        </div>
        <nav class="nav-links">
          <a href="#" class="nav-link">文档</a>
          <a href="#" class="nav-link">模型</a>
        </nav>
      </div>
    </header>

    <!-- Main Chat Area -->
    <main class="main-container">
      <div class="chat-container">
        
        <!-- Empty State -->
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-llama">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
              <circle cx="12" cy="12" r="4"/>
            </svg>
          </div>
          <h2 class="hero-title">开始使用 招标智脑 RAG</h2>
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

        <!-- Message List -->
        <div v-else class="message-list" ref="scrollContainer">
          <div v-for="(msg, index) in messages" :key="index" :class="['message-wrapper', msg.role]">
            <div class="message-avatar" v-if="msg.role === 'assistant'">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="4"/>
              </svg>
            </div>
            <div class="message-content">
              {{ msg.content }}
            </div>
          </div>
          <div v-if="loading" class="message-wrapper assistant">
            <div class="message-avatar">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <circle cx="12" cy="12" r="4"/>
              </svg>
            </div>
            <div class="message-content loading-indicator">
              <span>.</span><span>.</span><span>.</span>
            </div>
          </div>
        </div>

        <!-- Input Area -->
        <div class="input-wrapper">
          <div class="input-container">
            <input 
              type="text" 
              class="chat-input" 
              v-model="query" 
              placeholder="向 招标智脑 提问..." 
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
          <div class="input-footer">招标智脑 可能会产生误差。请考虑验证重要信息。</div>
        </div>

      </div>
    </main>
  </div>
</template>

<style scoped>
/* 
  Ollama-inspired Radical Minimalism 
  Binary radius: 12px (containers) / 9999px (interactive)
  Zero shadows. Grayscale only. 
*/

@font-face {
  font-family: 'SF Pro Rounded';
  src: local('SF Pro Rounded'), local('-apple-system');
  font-weight: 400 600;
}

.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #ffffff;
  color: #000000;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* --- Header --- */
.header {
  padding: 20px 32px;
  background-color: #ffffff;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1024px;
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

.nav-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.nav-link {
  color: #000000;
  text-decoration: none;
  font-size: 16px;
  font-weight: 400;
}

.nav-pill {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 8px 20px;
  font-size: 16px;
  font-weight: 400;
  cursor: pointer;
  background-color: #fafafa;
}

.nav-pill:hover {
  background-color: #e5e5e5;
}

/* --- Main Area --- */
.main-container {
  flex: 1;
  display: flex;
  justify-content: center;
  overflow: hidden;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  padding: 0 20px;
  position: relative;
}

/* --- Empty State --- */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding-bottom: 100px;
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
}

.suggestion-pill:hover {
  background-color: #e5e5e5;
  color: #000000;
}

/* --- Message List --- */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 40px 0 120px 0;
  display: flex;
  flex-direction: column;
  gap: 32px;
  scrollbar-width: none; /* Firefox */
}
.message-list::-webkit-scrollbar {
  display: none; /* Chrome/Safari/Edge */
}

.message-wrapper {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  max-width: 100%;
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
  border-radius: 12px;
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
.input-wrapper {
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
  border-radius: 50%;
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
