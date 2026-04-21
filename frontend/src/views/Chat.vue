<template>
<div class="chat-wrapper">
  <div class="header">
    <div class="logo">
      <div class="logo-mark">ZL</div>
      <span class="logo-name">智链<span class="logo-dot">·</span>问答</span>
    </div>

    <div class="header-center">
      <div class="kb-pills">
        <div v-for="(kb, idx) in kbPills" :key="idx" :class="['kb-pill', { on: kb.active }]" @click="toggleKb(idx)">
          <span class="kb-pill-dot" style="background:#000000"></span>{{ kb.name }}
        </div>
      </div>
    </div>

    <div class="header-right">
      <button class="history-btn" @click="sidebarOpen = !sidebarOpen">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        历史会话
      </button>
      <div class="avatar-btn" title="退出登录" @click="logout">{{ (currentUser.username || '陈').charAt(0).toUpperCase() }}</div>
    </div>
  </div>

  <div class="main" id="mainArea">

    <div class="sidebar" id="sidebar" v-show="sidebarOpen">
      <div class="sidebar-head">
        <button class="new-chat-btn" @click="startNewChat">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          新建会话
        </button>
      </div>
      <div class="hist-list">
        <div class="sidebar-section" v-if="todaySessions.length > 0">今天</div>
        <div v-for="session in todaySessions" :key="session.session_id" :class="['hist-item', { active: session.session_id === sessionId }]" @click="selectSession(session)">
          <div class="hist-q">{{ session.title || '新会话' }}</div>
          <div class="hist-meta">{{ formatTime(session.created_at) }} · 会话</div>
        </div>

        <div class="sidebar-section" v-if="earlierSessions.length > 0" style="padding-top:16px">更早</div>
        <div v-for="session in earlierSessions" :key="session.session_id" :class="['hist-item', { active: session.session_id === sessionId }]" @click="selectSession(session)">
          <div class="hist-q">{{ session.title || '新会话' }}</div>
          <div class="hist-meta">{{ formatDate(session.created_at) }} · 会话</div>
        </div>
        <div v-if="sessions.length === 0" style="padding: 16px; text-align: center; color: var(--text3); font-size: 12px;">暂无历史记录</div>
      </div>
    </div>

    <div class="chat-area" id="chatArea">
      <div class="messages" id="messages" ref="scrollContainer">
        <div class="msg-wrap">

          <div v-for="(msg, index) in messages" :key="index" :class="['msg', msg.role]">
            <div :class="['msg-av', msg.role]">{{ msg.role === 'assistant' ? 'Z' : (currentUser.username || '陈').charAt(0).toUpperCase() }}</div>
            <div class="msg-body">
              <div class="msg-name">{{ msg.role === 'assistant' ? '智链助手' : '我' }}</div>
              <div class="bubble">
                <div v-if="msg.role === 'user'">{{ msg.content }}</div>
                <div v-else class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
                
                <div class="sources" v-if="msg.role === 'assistant' && msg.sources && msg.sources.length > 0">
                  <div class="sources-lbl">参考来源 · {{ msg.sources.length }}条</div>
                  <span class="src-chip" v-for="(_src, idx) in msg.sources" :key="idx" @click="openSources(msg.sources || [])">
                    <span class="src-n">[{{ idx + 1 }}]</span>片段 {{ idx + 1 }}
                  </span>
                </div>
              </div>
              <div class="msg-feedback" v-if="msg.role === 'assistant' && index > 0">
                <button class="fb-btn" title="有帮助">👍</button>
                <button class="fb-btn" title="没帮助">👎</button>
                <span class="fb-copy">复制</span>
                <span class="fb-copy" v-if="msg.sources && msg.sources.length > 0" @click="openSources(msg.sources || [])">查看召回片段</span>
              </div>
            </div>
          </div>

          <div class="msg ai" id="typingMsg" v-if="loading && !isReceivingStream">
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

        </div>
      </div>

      <div style="background:var(--bg1);border-top:1px solid var(--border)">
        <div style="max-width:800px;margin:0 auto;padding:14px 28px 18px">
          <div class="input-box">
            <div class="input-row">
              <textarea class="chat-ta" id="chatInput" placeholder="输入问题…" rows="1"
                v-model="query" @keydown.enter.prevent="sendMessage" @input="autoResize" :disabled="loading"></textarea>
              <button class="send-btn" @click="sendMessage" :disabled="loading || !query.trim()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
              </button>
            </div>
            <div class="input-meta">
              <span class="meta-action">📎 附件</span>
              <span class="meta-sep">·</span>
              <span class="meta-action">✦ 改写</span>
              <span class="meta-sep">·</span>
              <span class="meta-action" @click="chunkPanelOpen = !chunkPanelOpen">⊞ 召回片段</span>
              <span class="mode-tag">混合检索</span>
            </div>
          </div>
          <div style="text-align:center;font-size:11px;color:var(--text3);margin-top:8px;font-family:var(--mono)">
            Enter 发送 · Shift+Enter 换行 · 内容基于知识库生成，仅供参考
          </div>
        </div>
      </div>
    </div>

  </div>

  <div :class="['chunk-panel', { open: chunkPanelOpen }]" id="chunkPanel">
    <div class="panel-head">
      <span class="panel-title">召回片段 · {{ currentSources.length }}条</span>
      <button class="panel-close" @click="chunkPanelOpen = false">✕</button>
    </div>
    <div class="chunk-list">
      <div class="chunk-card" v-for="(_src, idx) in currentSources" :key="idx">
        <div class="chunk-card-head">
          <span class="chunk-source">[{{ idx + 1 }}] 检索片段</span>
          <span class="chunk-score">相关</span>
        </div>
        <div class="chunk-text">{{ _src }}</div>
      </div>
      <div v-if="currentSources.length === 0" style="text-align: center; color: var(--text3); margin-top: 40px; font-size: 12px;">暂无片段信息</div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import request from '../api/request'
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
  } catch (error) { console.error('获取历史记录失败', error) }
}

onMounted(() => {
  fetchHistory()
  if (messages.value.length === 0) {
    messages.value.push({
      role: 'assistant',
      content: '您好！当前已接入 **政策法规** 和 **企业信息** 知识库，采用混合检索模式。<br>请直接输入您的问题，我会为您检索相关内容并给出准确答复。'
    })
  }
})

const startNewChat = () => {
  sessionId.value = null
  messages.value = [{
    role: 'assistant',
    content: '新会话已开始，请输入您的问题。'
  }]
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

const kbPills = ref([
  { name: '政策法规', active: true },
  { name: '企业信息', active: true },
  { name: '商品信息', active: false },
  { name: '招标信息', active: false }
])

const toggleKb = (index: number) => {
  kbPills.value[index].active = !kbPills.value[index].active
}

const todaySessions = computed(() => {
  return sessions.value.filter(s => {
    const d = new Date(s.created_at)
    const today = new Date()
    return d.getDate() === today.getDate() && d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear()
  })
})

const earlierSessions = computed(() => {
  return sessions.value.filter(s => {
    const d = new Date(s.created_at)
    const today = new Date()
    return !(d.getDate() === today.getDate() && d.getMonth() === today.getMonth() && d.getFullYear() === today.getFullYear())
  })
})

const formatTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
}
const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString()
}
</script>

<style scoped>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Noto+Sans+SC:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:      #f5f4f0;
  --bg1:     #ffffff;
  --bg2:     #f0ede8;
  --bg3:     #e8e4de;
  --border:  #e2ddd7;
  --border-h:#c8c2ba;
  --text0:   #1a1714;
  --text1:   #4a4540;
  --text2:   #8a837a;
  --text3:   #b8b2aa;
  --accent:  #2563eb;
  --accent-h:#1d4ed8;
  --accent-l:#eff6ff;
  --accent2: #059669;
  --accent2-l:#f0fdf4;
  --warn:    #d97706;
  --sans:    'DM Sans', 'Noto Sans SC', sans-serif;
  --mono:    'JetBrains Mono', monospace;
  --r:       8px;
  --r-lg:    12px;
  --shadow:  0 1px 3px rgba(0,0,0,.06), 0 1px 2px rgba(0,0,0,.04);
  --shadow-md: 0 4px 12px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.04);
}

*{margin:0;padding:0;box-sizing:border-box}
html{font-size:14px}
body{background:var(--bg);color:var(--text0);font-family:var(--sans);height:100vh;display:flex;flex-direction:column;overflow:hidden}

/* ── Header ── */
.header{
  height:52px;background:var(--bg1);border-bottom:1px solid var(--border);
  display:flex;align-items:center;padding:0 20px;gap:16px;flex-shrink:0;
  
}
.logo{display:flex;align-items:center;gap:10px}
.logo-mark{
  width:30px;height:30px;border-radius:8px;
  background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  font-family:var(--mono);font-size:11px;font-weight:500;color:#fff;letter-spacing:-0.5px;
}
.logo-name{font-size:15px;font-weight:600;color:var(--text0);letter-spacing:-.01em}
.logo-dot{color:var(--text0)}

.header-center{flex:1;display:flex;justify-content:center}
.kb-pills{display:flex;gap:6px}
.kb-pill{
  display:flex;align-items:center;gap:6px;padding:5px 12px;
  border-radius:20px;border:1px solid var(--border);background:var(--bg);
  font-size:12px;color:var(--text2);cursor:pointer;transition:all .15s;
  user-select:none;
}
.kb-pill:hover{border-color:var(--border-h);color:var(--text1)}
.kb-pill.on{background:var(--bg2);border-color:rgba(37,99,235,.25);color:var(--text0);font-weight:500}
.kb-pill-dot{width:6px;height:6px;border-radius: 9999px;align-items:center;gap:10px;margin-left:auto}
.avatar-btn{
  width:32px;height:32px;border-radius:50%;
  background:var(--accent);
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:600;color:#fff;cursor:pointer;border:2px solid var(--bg1);
  
}
.history-btn{
  padding:5px 12px;border-radius:6px;border:1px solid var(--border);
  background:var(--bg1);color:var(--text1);font-size:12px;cursor:pointer;
  font-family:var(--sans);transition:all .15s;display:flex;align-items:center;gap:5px;
}
.history-btn:hover{border-color:var(--border-h);color:var(--text0)}

/* ── Main layout ── */
.main{flex:1;display:flex;overflow:hidden}

/* ── Sidebar ── */
.sidebar{
  width:268px;flex-shrink:0;background:var(--bg1);border-right:1px solid var(--border);
  display:flex;flex-direction:column;overflow:hidden;
}
.sidebar-head{
  padding:16px;border-bottom:1px solid var(--border);
}
.new-chat-btn{
  width:100%;padding:9px 0;border-radius:var(--r);
  background:var(--accent);color:#fff;border:none;
  font-family:var(--sans);font-size:13px;font-weight:500;cursor:pointer;
  transition:background .15s;display:flex;align-items:center;justify-content:center;gap:7px;
}
.new-chat-btn:hover{background:var(--accent-h)}
.new-chat-btn svg{width:14px;height:14px}

.sidebar-section{padding:12px 16px 4px;font-size:10px;font-family:var(--mono);color:var(--text3);letter-spacing:.1em;text-transform:uppercase}
.hist-list{flex:1;overflow-y:auto;padding:4px 8px 16px}
.hist-item{
  padding:9px 10px;border-radius:var(--r);cursor:pointer;
  transition:background .12s;margin-bottom:2px;
  border:1px solid transparent;
}
.hist-item:hover{background:var(--bg2)}
.hist-item.active{background:var(--bg2);border-color:var(--text0)}
.hist-q{font-size:12px;color:var(--text0);line-height:1.45;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:400}
.hist-item.active .hist-q{color:var(--text0)}
.hist-meta{font-size:10px;color:var(--text3);margin-top:3px;font-family:var(--mono)}

/* ── Chat area ── */
.chat-area{flex:1;display:flex;flex-direction:column;overflow:hidden}
.messages{flex:1;overflow-y:auto;padding:28px 0}
.msg-wrap{max-width:800px;margin:0 auto;padding:0 28px}

.msg{display:flex;gap:12px;margin-bottom:22px}
.msg.user{flex-direction:row-reverse}
.msg-av{
  width:32px;height:32px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;
}
.msg-av.ai{background:var(--accent);color:#fff}
.msg-av.user{background:var(--accent);color:#fff}

.msg-body{max-width:78%}
.msg-name{font-size:11px;color:var(--text2);margin-bottom:4px;font-family:var(--mono)}
.msg.user .msg-name{text-align:right}
.bubble{
  padding:12px 16px;border-radius:12px;font-size:13.5px;line-height:1.75;
}
.msg.ai .bubble{background:var(--bg1);border:1px solid var(--border);border-top-left-radius:3px}
.msg.user .bubble{background:var(--accent);color:#fff;border-top-right-radius:3px}

.bubble strong{font-weight:600}
.bubble p{margin-bottom:8px}
.bubble p:last-child{margin-bottom:0}
.bubble ul{padding-left:18px;margin:6px 0}
.bubble ul li{margin-bottom:3px}

.sources{margin-top:10px;padding-top:10px;border-top:1px solid var(--border)}
.sources-lbl{font-size:10px;color:var(--text3);font-family:var(--mono);letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px}
.src-chip{
  display:inline-flex;align-items:center;gap:4px;padding:3px 8px;
  border-radius:4px;margin:2px 3px 2px 0;
  background:var(--bg2);border:1px solid var(--border);
  font-size:11px;color:var(--text1);cursor:pointer;font-family:var(--mono);
  transition:all .12s;
}
.src-chip:hover{border-color:var(--text0);color:var(--text0);background:var(--bg2)}
.src-n{color:var(--text0);font-weight:500}

/* typing */
.typing{display:flex;align-items:center;gap:5px;padding:14px 16px}
.typing-dot{width:5px;height:5px;border-radius:50%;background:var(--text3);animation:tdot 1.3s infinite}
.typing-dot:nth-child(2){animation-delay:.15s}
.typing-dot:nth-child(3){animation-delay:.3s}
@keyframes tdot{0%,60%,100%{opacity:.3;transform:scale(.8)}30%{opacity:1;transform:scale(1)}}

/* feedback row */
.msg-feedback{display:flex;gap:8px;margin-top:6px;align-items:center}
.fb-btn{
  width:26px;height:26px;border-radius:5px;border:1px solid var(--border);background:var(--bg1);
  display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:13px;
  transition:all .12s;color:var(--text2);
}
.fb-btn:hover{border-color:var(--border-h);color:var(--text0)}
.fb-copy{
  font-size:11px;color:var(--text3);cursor:pointer;padding:2px 6px;border-radius:4px;
  transition:all .12s;font-family:var(--mono);
}
.fb-copy:hover{color:var(--text1);background:var(--bg2)}

/* ── Input area ── */
.input-area{
  padding:16px 28px 20px;border-top:1px solid var(--border);background:var(--bg1);
  max-width:800px;width:100%;margin:0 auto;box-sizing:border-box;
  align-self:center;width:100%;
}
.input-box{
  background:var(--bg1);border:1.5px solid var(--border);border-radius:12px;
  padding:12px 14px;transition:border-color .15s;
}
.input-box:focus-within{border-color:var(--text0);}
.input-row{display:flex;align-items:flex-end;gap:10px}
.chat-ta{
  flex:1;border:none;outline:none;resize:none;background:transparent;
  color:var(--text0);font-size:14px;font-family:var(--sans);line-height:1.6;
  min-height:22px;max-height:130px;
}
.chat-ta::placeholder{color:var(--text3)}
.send-btn{
  width:34px;height:34px;border-radius:8px;background:var(--accent);border:none;
  cursor:pointer;display:flex;align-items:center;justify-content:center;
  color:#fff;flex-shrink:0;transition:all .15s;
}
.send-btn:hover{background:var(--accent-h);transform:scale(1.04)}
.send-btn svg{width:15px;height:15px}

.input-meta{display:flex;align-items:center;gap:2px;margin-top:8px}
.meta-action{
  display:flex;align-items:center;gap:5px;padding:4px 8px;border-radius:5px;
  font-size:11px;color:var(--text2);cursor:pointer;transition:all .12s;font-family:var(--mono);
}
.meta-action:hover{background:var(--bg2);color:var(--text1)}
.meta-sep{color:var(--border);padding:0 2px}
.mode-tag{
  margin-left:auto;font-size:10px;font-family:var(--mono);
  padding:2px 8px;border-radius:4px;background:var(--bg2);color:var(--text0);
  border:1px solid rgba(37,99,235,.15);
}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--bg3);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:var(--border-h)}

/* ── Right panel: chunk viewer (slide-in) ── */
.chunk-panel{
  width:340px;flex-shrink:0;border-left:1px solid var(--border);
  background:var(--bg1);display:flex;flex-direction:column;
  transform:translateX(100%);transition:transform .25s ease;
  position:absolute;right:0;top:52px;bottom:0;z-index:10;
  
}
.chunk-panel.open{transform:translateX(0)}
.panel-head{
  padding:16px 18px;border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.panel-title{font-size:13px;font-weight:600;color:var(--text0)}
.panel-close{
  width:26px;height:26px;border-radius:5px;border:1px solid var(--border);
  background:transparent;cursor:pointer;display:flex;align-items:center;justify-content:center;
  color:var(--text2);font-size:14px;transition:all .12s;
}
.panel-close:hover{background:var(--bg2);color:var(--text0)}
.chunk-list{flex:1;overflow-y:auto;padding:12px}
.chunk-card{
  background:var(--bg);border:1px solid var(--border);border-radius:var(--r);
  padding:12px;margin-bottom:8px;transition:border-color .12s;cursor:default;
}
.chunk-card:hover{border-color:var(--border-h)}
.chunk-card-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:7px}
.chunk-source{font-family:var(--mono);font-size:10px;color:var(--text0);font-weight:500}
.chunk-score{
  font-family:var(--mono);font-size:10px;padding:1px 6px;border-radius:3px;
  background:var(--accent2-l);color:var(--accent2);border:1px solid var(--border);
}
.chunk-text{font-size:12px;color:var(--text1);line-height:1.65}
.chunk-meta{font-size:10px;color:var(--text3);margin-top:6px;font-family:var(--mono)}

.chat-wrapper { height: 100vh; display: flex; flex-direction: column; overflow: hidden; background: var(--bg); color: var(--text0); font-family: var(--sans); }
.markdown-body { font-size: 14.5px; line-height: 1.6; }
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) { margin-top: 1.5em; margin-bottom: 0.5em; font-family: var(--sans); font-weight: 500; }
.markdown-body :deep(p) { margin-bottom: 1em; }
.markdown-body :deep(ul) { padding-left: 20px; margin-bottom: 1em; }
.markdown-body :deep(li) { margin-bottom: 0.25em; }
</style>
