<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'
import BrandMark from '../components/BrandMark.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const currentUser = ref(JSON.parse(localStorage.getItem('current_user') || '{}'))

marked.setOptions({ breaks: true, gfm: true })
const renderMarkdown = (text: string) => {
  if (!text) return ''
  return DOMPurify.sanitize(marked(text) as string)
}

const query = ref('')
const messages = ref<{role: string, content: string, sources?: any[]}[]>([])
const loading = ref(false)
const isReceivingStream = ref(false)
const sessionId = ref<string | null>(null)
const sessions = ref<any[]>([])
const scrollContainer = ref<HTMLElement | null>(null)
const sidebarOpen = ref(true)
const chunkPanelOpen = ref(false)
const currentSources = ref<any[]>([])

const fetchHistory = async () => {
  try {
    const res: any = await request.get('/chat/history')
    sessions.value = res || []
  } catch (error) {
    console.error('获取历史记录失败', error)
  }
}

onMounted(() => fetchHistory())

const startNewChat = () => {
  sessionId.value = null
  messages.value = []
  chunkPanelOpen.value = false
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
    content: m.content,
    sources: m.sources || []
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

const autoResize = (event: Event) => {
  const el = event.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 130) + 'px'
}

const openSources = (sources: any[]) => {
  currentSources.value = sources
  chunkPanelOpen.value = true
}

const sendMessage = async () => {
  if (!query.value.trim() || loading.value) return
  
  const userMsg = query.value
  messages.value.push({ role: 'user', content: userMsg })
  query.value = ''
  
  const textarea = document.querySelector('.chat-ta') as HTMLTextAreaElement
  if (textarea) textarea.style.height = 'auto'

  loading.value = true
  isReceivingStream.value = false
  scrollToBottom()
  
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      body: JSON.stringify({ query: userMsg, session_id: sessionId.value, domain: 'bidding' })
    })

    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        logout()
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder('utf-8')
    let done = false
    let isFirstChunk = true
    let currentAssistantMsgIndex = -1

    while (reader && !done) {
      const { value, done: readerDone } = await reader.read()
      done = readerDone
      if (value) {
        const chunkStr = decoder.decode(value, { stream: true })
        const lines = chunkStr.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'meta') {
                sessionId.value = data.session_id
                messages.value.push({ role: 'assistant', content: '', sources: data.sources || [] })
                currentAssistantMsgIndex = messages.value.length - 1
              } else if (data.type === 'chunk') {
                if (isFirstChunk) { isReceivingStream.value = true; isFirstChunk = false; }
                if (currentAssistantMsgIndex !== -1) {
                  messages.value[currentAssistantMsgIndex].content += data.chunk
                } else {
                  messages.value.push({ role: 'assistant', content: data.chunk })
                  currentAssistantMsgIndex = messages.value.length - 1
                }
                scrollToBottom()
              } else if (data.type === 'error') {
                if (currentAssistantMsgIndex !== -1) messages.value[currentAssistantMsgIndex].content += '\n\n' + data.error
                else messages.value.push({ role: 'assistant', content: data.error })
              }
            } catch (e) { console.error('Error parsing stream', e, line) }
          }
        }
      }
    }
    await fetchHistory()
  } catch (error) {
    messages.value.push({ role: 'assistant', content: '请求失败或超时，请重试。' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-wrapper">
    <!-- Topbar -->
    <header class="header">
      <div class="logo">
        <BrandMark :size="24" class="logo-mark" />
        <span class="logo-name">智能问答平台</span>
      </div>

      <div class="header-center">
        <div class="kb-pills">
          <div class="kb-pill on">
            <span class="kb-pill-dot" style="background:var(--c-black)"></span>全部知识库
          </div>
        </div>
      </div>

      <div class="header-right">
        <button class="history-btn" @click="sidebarOpen = !sidebarOpen">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          历史会话
        </button>
        <div class="avatar-btn" :title="currentUser.username" @click="logout">
          {{ (currentUser.username || 'U').charAt(0).toUpperCase() }}
        </div>
      </div>
    </header>

    <div class="main-layout">
      <!-- Sidebar -->
      <aside class="sidebar" v-show="sidebarOpen">
        <div class="sidebar-head">
          <button class="new-chat-btn" @click="startNewChat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            新建会话
          </button>
        </div>
        <div class="hist-list">
          <div class="sidebar-section" v-if="sessions.length > 0">近期会话</div>
          <div 
            v-for="session in sessions" 
            :key="session.session_id" 
            :class="['hist-item', { active: session.session_id === sessionId }]"
            @click="selectSession(session)"
          >
            <div class="hist-q">{{ session.title || '新会话' }}</div>
            <div class="hist-meta">{{ new Date(session.created_at || Date.now()).toLocaleDateString() }}</div>
          </div>
          <div v-if="sessions.length === 0" class="empty-history">
            暂无历史会话
          </div>
        </div>
      </aside>

      <!-- Chat Area -->
      <main class="chat-area">
        <div class="messages" ref="scrollContainer">
          <div class="msg-wrap">
            
            <!-- Empty State -->
            <div v-if="messages.length === 0" class="empty-state">
              <BrandMark :size="48" class="empty-logo" />
              <h2 class="hero-title">开始检索业务知识</h2>
              <p class="hero-subtitle">基于企业招投标数据、政策法规与商品信息的智能问答</p>
              <div class="suggestion-grid">
                <button class="suggestion-pill" @click="query = '查询北京科技有限公司的工商信息'; sendMessage()">查询企业信息</button>
                <button class="suggestion-pill" @click="query = '最近有哪些高性能服务器的招标项目？'; sendMessage()">查找招标项目</button>
                <button class="suggestion-pill" @click="query = '中华人民共和国招标投标法的核心内容是什么？'; sendMessage()">检索政策法规</button>
              </div>
            </div>

            <!-- Messages -->
            <template v-else>
              <div v-for="(msg, index) in messages" :key="index" :class="['msg', msg.role]">
                <div :class="['msg-av', msg.role]">
                  {{ msg.role === 'assistant' ? 'Z' : (currentUser.username || 'U').charAt(0).toUpperCase() }}
                </div>
                <div class="msg-body">
                  <div class="msg-name">{{ msg.role === 'assistant' ? '智链助手' : '我' }}</div>
                  <div class="bubble">
                    <div v-if="msg.role === 'user'" class="user-text">{{ msg.content }}</div>
                    <div v-else class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
                    
                    <div class="sources" v-if="msg.role === 'assistant' && msg.sources && msg.sources.length > 0">
                      <div class="sources-lbl">参考来源 · {{ msg.sources.length }}条</div>
                      <span class="src-chip" @click="openSources(msg.sources || [])">
                        查看检索片段
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Loading State -->
              <div class="msg ai" v-if="loading && !isReceivingStream">
                <div class="msg-av ai">Z</div>
                <div class="msg-body">
                  <div class="msg-name">智链助手</div>
                  <div class="bubble">
                    <div class="typing">
                      <div class="typing-dot"></div>
                      <div class="typing-dot"></div>
                      <div class="typing-dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            </template>

          </div>
        </div>

        <!-- Input Area -->
        <div class="input-area">
          <div class="input-box">
            <div class="input-row">
              <textarea 
                class="chat-ta" 
                id="chatInput" 
                placeholder="输入问题…" 
                rows="1"
                v-model="query"
                @keydown.enter.prevent="sendMessage"
                @input="autoResize"
                :disabled="loading"
              ></textarea>
              <button class="send-btn" @click="sendMessage" :disabled="loading || !query.trim()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
            <div class="input-meta">
              <span class="mode-tag">混合检索</span>
            </div>
          </div>
          <div class="input-footer">
            Enter 发送 · Shift+Enter 换行 · 内容基于知识库生成，仅供参考
          </div>
        </div>
      </main>

      <!-- Chunk Panel (Right Sidebar) -->
      <aside :class="['chunk-panel', { open: chunkPanelOpen }]">
        <div class="panel-head">
          <span class="panel-title">召回片段 · {{ currentSources.length }}条</span>
          <button class="panel-close" @click="chunkPanelOpen = false">✕</button>
        </div>
        <div class="chunk-list">
          <div class="chunk-card" v-for="(src, idx) in currentSources" :key="idx">
            <div class="chunk-card-head">
              <span class="chunk-source">片段 {{ idx + 1 }}</span>
            </div>
            <div class="chunk-text">{{ src }}</div>
          </div>
          <div v-if="currentSources.length === 0" class="empty-history" style="text-align: center; margin-top: 40px;">
            暂无片段信息
          </div>
        </div>
      </aside>

    </div>
  </div>
</template>

<style scoped>
.app-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: var(--c-white);
  color: var(--c-black);
}

/* --- Header --- */
.header {
  height: 52px;
  border-bottom: 1px solid var(--c-light-gray);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--c-white);
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-mark {
  color: var(--c-black);
}

.logo-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.kb-pills {
  display: flex;
  gap: 8px;
}

.kb-pill {
  padding: 4px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--c-light-gray);
  background: var(--c-snow);
  color: var(--c-stone);
  font-size: 12px;
  font-family: var(--font-body);
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all 0.15s;
}

.kb-pill.on {
  border-color: var(--c-black);
  color: var(--c-black);
  background: var(--c-white);
}

.kb-pill-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.history-btn {
  padding: 5px 12px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--c-light-gray);
  background: var(--c-white);
  color: var(--c-near-black);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.15s;
}

.history-btn:hover {
  border-color: var(--c-black);
  background: var(--c-snow);
}

.avatar-btn {
  width: 30px;
  height: 30px;
  border-radius: var(--radius-pill);
  background: var(--c-snow);
  border: 1px solid var(--c-light-gray);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: var(--c-black);
  cursor: pointer;
  transition: background 0.15s;
}

.avatar-btn:hover {
  background: var(--c-light-gray);
}

/* --- Main Layout --- */
.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* --- Sidebar --- */
.sidebar {
  width: 268px;
  flex-shrink: 0;
  background: var(--c-snow);
  border-right: 1px solid var(--c-light-gray);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-head {
  padding: 16px;
  border-bottom: 1px solid var(--c-light-gray);
}

.new-chat-btn {
  width: 100%;
  padding: 10px 0;
  border-radius: var(--radius-pill);
  background: var(--c-white);
  color: var(--c-black);
  border: 1px solid var(--c-light-gray);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.new-chat-btn:hover {
  background: var(--c-black);
  color: var(--c-white);
  border-color: var(--c-black);
}

.new-chat-btn svg {
  width: 14px;
  height: 14px;
}

.sidebar-section {
  padding: 16px 16px 4px;
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--c-stone);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.hist-list {
  flex: 1;
  overflow-y: auto;
  padding: 4px 8px 16px;
}

.hist-item {
  padding: 10px 12px;
  border-radius: var(--radius-pill);
  cursor: pointer;
  transition: background 0.12s;
  margin-bottom: 2px;
  border: 1px solid transparent;
}

.hist-item:hover {
  background: var(--c-light-gray);
}

.hist-item.active {
  background: var(--c-black);
  color: var(--c-white);
}

.hist-q {
  font-size: 13px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
}

.hist-item.active .hist-q {
  color: var(--c-white);
  font-weight: 500;
}

.hist-meta {
  font-size: 10px;
  color: var(--c-stone);
  margin-top: 4px;
  font-family: var(--font-mono);
}

.hist-item.active .hist-meta {
  color: var(--c-silver);
}

.empty-history {
  padding: 16px;
  text-align: center;
  font-size: 12px;
  color: var(--c-silver);
}

/* --- Chat Area --- */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--c-white);
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 32px 0;
}

.msg-wrap {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10vh 0;
  text-align: center;
}

.empty-logo {
  color: var(--c-black);
  margin-bottom: 24px;
}

.hero-title {
  font-size: 28px;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  color: var(--c-stone);
  margin-bottom: 40px;
  font-size: 15px;
}

.suggestion-grid {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-pill {
  padding: 10px 20px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--c-light-gray);
  background: var(--c-white);
  color: var(--c-near-black);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-pill:hover {
  border-color: var(--c-black);
  background: var(--c-snow);
}

/* Messages */
.msg {
  display: flex;
  gap: 16px;
}

.msg.user {
  flex-direction: row-reverse;
}

.msg-av {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-pill);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid var(--c-light-gray);
}

.msg-av.ai {
  background: var(--c-black);
  color: var(--c-white);
  border: none;
}

.msg-av.user {
  background: var(--c-snow);
  color: var(--c-black);
}

.msg-body {
  max-width: 80%;
}

.msg-name {
  font-size: 11px;
  color: var(--c-stone);
  margin-bottom: 6px;
  font-family: var(--font-mono);
}

.msg.user .msg-name {
  text-align: right;
}

.bubble {
  font-size: 14.5px;
  line-height: 1.6;
}

.user .bubble {
  background: var(--c-snow);
  border: 1px solid var(--c-light-gray);
  padding: 12px 18px;
  border-radius: 20px 20px 4px 20px;
  color: var(--c-black);
}

.ai .bubble {
  background: transparent;
  color: var(--c-black);
  padding: 4px 0;
}

.sources {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--c-light-gray);
}

.sources-lbl {
  font-size: 10px;
  color: var(--c-stone);
  font-family: var(--font-mono);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.src-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: var(--c-snow);
  border: 1px solid var(--c-light-gray);
  font-size: 11px;
  color: var(--c-near-black);
  cursor: pointer;
  font-family: var(--font-mono);
  transition: all 0.15s;
}

.src-chip:hover {
  border-color: var(--c-black);
  background: var(--c-white);
}

/* Typing */
.typing {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 0;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--c-stone);
  animation: tdot 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes tdot {
  0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* --- Input Area --- */
.input-area {
  padding: 16px 28px 24px;
  background: linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,1) 20%);
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  box-sizing: border-box;
}

.input-box {
  background: var(--c-white);
  border: 1px solid var(--c-light-gray);
  border-radius: var(--radius-container);
  padding: 12px 16px;
  transition: border-color 0.2s;
}

.input-box:focus-within {
  border-color: var(--c-black);
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.chat-ta {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  color: var(--c-black);
  font-size: 15px;
  font-family: var(--font-body);
  line-height: 1.5;
  min-height: 24px;
  max-height: 160px;
  padding: 0;
}

.chat-ta::placeholder {
  color: var(--c-silver);
}

.send-btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-pill);
  background: var(--c-black);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-white);
  flex-shrink: 0;
  transition: opacity 0.15s;
}

.send-btn:disabled {
  background: var(--c-light-gray);
  color: var(--c-silver);
  cursor: not-allowed;
}

.send-btn:not(:disabled):hover {
  opacity: 0.8;
}

.send-btn svg {
  width: 16px;
  height: 16px;
}

.input-meta {
  display: flex;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--c-snow);
}

.mode-tag {
  margin-left: auto;
  font-size: 10px;
  font-family: var(--font-mono);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  background: var(--c-snow);
  color: var(--c-stone);
  border: 1px solid var(--c-light-gray);
}

.input-footer {
  text-align: center;
  font-size: 11px;
  color: var(--c-silver);
  margin-top: 12px;
  font-family: var(--font-mono);
}

/* --- Chunk Panel --- */
.chunk-panel {
  width: 360px;
  flex-shrink: 0;
  border-left: 1px solid var(--c-light-gray);
  background: var(--c-snow);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  z-index: 10;
}

.chunk-panel.open {
  transform: translateX(0);
}

.panel-head {
  padding: 20px 24px;
  border-bottom: 1px solid var(--c-light-gray);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--c-white);
}

.panel-title {
  font-size: 14px;
  font-weight: 500;
  font-family: var(--font-display);
}

.panel-close {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-pill);
  border: 1px solid var(--c-light-gray);
  background: var(--c-white);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--c-stone);
  transition: all 0.15s;
}

.panel-close:hover {
  background: var(--c-snow);
  color: var(--c-black);
  border-color: var(--c-black);
}

.chunk-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.chunk-card {
  background: var(--c-white);
  border: 1px solid var(--c-light-gray);
  border-radius: var(--radius-container);
  padding: 16px;
  margin-bottom: 12px;
}

.chunk-card-head {
  margin-bottom: 8px;
}

.chunk-source {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--c-stone);
}

.chunk-text {
  font-size: 13px;
  color: var(--c-near-black);
  line-height: 1.6;
  white-space: pre-wrap;
}

/* Markdown overrides */
.markdown-body {
  font-size: 14.5px;
  line-height: 1.6;
}
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-family: var(--font-display);
}
.markdown-body :deep(p) {
  margin-bottom: 1em;
}
.markdown-body :deep(ul) {
  padding-left: 20px;
  margin-bottom: 1em;
}
.markdown-body :deep(li) {
  margin-bottom: 0.25em;
}
</style>
