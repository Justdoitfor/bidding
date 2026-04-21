<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import request from '../api/request'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const currentUser = ref(JSON.parse(localStorage.getItem('admin_current_user') || '{}'))
const renderMarkdown = (text: string) => DOMPurify.sanitize(marked(text) as string)

const activeTab = ref('dashboard')

const historyData = ref<any[]>([])
const usersData = ref<any[]>([])
const searchSession = ref('')
const searchUser = ref('')
const dialogVisible = ref(false)
const currentMessages = ref<any[]>([])
const selectedSessionTitle = ref('')

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
  } catch (error) { console.error(error) }
}

const fetchUsers = async () => {
  try {
    const res: any = await request.get('/users')
    usersData.value = res || []
  } catch (error) { console.error(error) }
}

const toggleUserStatus = async (user: any) => {
  if (!confirm(`确定要${user.is_active ? '禁用' : '启用'}用户 ${user.username} 吗？`)) return
  try {
    await request.patch(`/users/${user.id}`, { is_active: !user.is_active })
    fetchUsers()
  } catch (error) { console.error(error) }
}

const deleteUser = async (user: any) => {
  if (!confirm(`确定要永久删除用户 ${user.username} 吗？`)) return
  try {
    await request.delete(`/users/${user.id}`)
    fetchUsers()
    fetchAllHistory()
  } catch (error) { console.error(error) }
}

onMounted(() => {
  fetchAllHistory()
  fetchUsers()
})

const filteredSessions = computed(() => {
  if (!searchSession.value) return historyData.value
  const q = searchSession.value.toLowerCase()
  return historyData.value.filter(item => (item.username || item.user_id || '').toLowerCase().includes(q))
})

const filteredUsers = computed(() => {
  if (!searchUser.value) return usersData.value
  const q = searchUser.value.toLowerCase()
  return usersData.value.filter(item => (item.username || item.id || '').toLowerCase().includes(q))
})

const viewSession = (row: any) => {
  selectedSessionTitle.value = row.title || '会话详情'
  currentMessages.value = row.messages || []
  dialogVisible.value = true
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="dashboard-wrapper">
    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'dashboard' }]" @click="activeTab = 'dashboard'">仪表盘</button>
      <button :class="['tab-btn', { active: activeTab === 'docs' }]" @click="activeTab = 'docs'">会话记录</button>
      <button :class="['tab-btn', { active: activeTab === 'users' }]" @click="activeTab = 'users'">用户管理</button>
      <button :class="['tab-btn', { active: activeTab === 'settings' }]" @click="activeTab = 'settings'">系统设置</button>
    </div>

    <!-- Dashboard View -->
    <div v-if="activeTab === 'dashboard'" class="view-panel">
      <div class="grid-4">
        <div class="stat-card">
          <div class="stat-title">总提问次数</div>
          <div class="stat-val">12,482</div>
          <div class="stat-trend up">↑ 14% 较上周</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">活跃用户</div>
          <div class="stat-val">842</div>
          <div class="stat-trend up">↑ 5% 较上周</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">知识库文档</div>
          <div class="stat-val">3,291</div>
          <div class="stat-trend neutral">- 持平</div>
        </div>
        <div class="stat-card">
          <div class="stat-title">平均检索延迟</div>
          <div class="stat-val">142ms</div>
          <div class="stat-trend down">↓ 12ms 较上周</div>
        </div>
      </div>
      
      <div class="grid-2" style="margin-top: 24px;">
        <div class="panel-card">
          <div class="card-head">系统负载监控</div>
          <div class="placeholder-chart">CPU/内存监控占位图</div>
        </div>
        <div class="panel-card">
          <div class="card-head">热门检索词</div>
          <div class="placeholder-chart">关键词词云占位图</div>
        </div>
      </div>
    </div>

    <!-- Sessions View -->
    <div v-if="activeTab === 'docs'" class="view-panel">
      <div class="panel-card">
        <div class="toolbar">
          <input type="text" class="form-input" v-model="searchSession" placeholder="搜索用户名或会话..." style="width: 300px;" />
          <button class="btn" style="margin-left:auto" @click="fetchAllHistory">刷新记录</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>会话 ID</th>
              <th>用户</th>
              <th>主题</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filteredSessions" :key="row.session_id">
              <td class="mono">{{ row.session_id.substring(0,8) }}</td>
              <td>{{ row.username }}</td>
              <td>{{ row.title }}</td>
              <td class="muted">{{ formatDate(row.created_at) }}</td>
              <td><button class="btn" @click="viewSession(row)">查看详情</button></td>
            </tr>
            <tr v-if="filteredSessions.length === 0">
              <td colspan="5" style="text-align: center; padding: 32px; color: var(--c-silver);">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Users View -->
    <div v-if="activeTab === 'users'" class="view-panel">
      <div class="panel-card">
        <div class="toolbar">
          <input type="text" class="form-input" v-model="searchUser" placeholder="搜索用户名..." style="width: 300px;" />
          <button class="btn primary" style="margin-left:auto" @click="fetchUsers">刷新用户</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>用户 ID</th>
              <th>用户名</th>
              <th>角色</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td class="mono">{{ user.id.substring(0,8) }}</td>
              <td>{{ user.username }}</td>
              <td><span :class="['role-pill', user.is_admin ? 'admin' : 'user']">{{ user.is_admin ? '管理员' : '普通用户' }}</span></td>
              <td>
                <span :class="['status-dot', user.is_active ? 'active' : 'inactive']"></span>
                {{ user.is_active ? '正常' : '禁用' }}
              </td>
              <td>
                <div class="action-btns" v-if="user.id !== currentUser.id">
                  <button class="btn" @click="toggleUserStatus(user)">{{ user.is_active ? '禁用' : '启用' }}</button>
                  <button class="btn danger" @click="deleteUser(user)">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Settings View -->
    <div v-if="activeTab === 'settings'" class="view-panel">
      <div class="panel-card">
        <div class="card-head">系统配置</div>
        <div class="form-grid">
          <div class="form-group">
            <label>平台名称</label>
            <input class="form-input" value="招投标信息智能问答平台" />
          </div>
          <div class="form-group">
            <label>最大历史记录保留天数</label>
            <input class="form-input" type="number" value="30" />
          </div>
          <div class="form-group">
            <label>系统提示词 (System Prompt)</label>
            <textarea class="form-textarea">你是一个专业的招投标与企业信息问答助手...</textarea>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Bubbles Modal -->
    <div class="modal-overlay" v-if="dialogVisible" @click.self="dialogVisible = false">
      <div class="modal">
        <div class="modal-head">
          <div><div class="modal-title">{{ selectedSessionTitle }}</div></div>
          <button class="modal-close" @click="dialogVisible = false">✕</button>
        </div>
        <div class="modal-body chat-bubbles">
          <div v-for="(msg, idx) in currentMessages" :key="idx" :class="['bubble-wrap', msg.role]">
            <div class="bubble-av" v-if="msg.role === 'assistant'">Z</div>
            <div class="bubble-content">
              <div class="bubble-text markdown-body" v-if="msg.role === 'assistant'" v-html="renderMarkdown(msg.content)"></div>
              <div class="bubble-text user-text" v-else>{{ msg.content }}</div>
            </div>
            <div class="bubble-av user" v-if="msg.role === 'user'">U</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--c-light-gray);
  padding-bottom: 8px;
}
.tab-btn {
  background: none; border: none; font-family: var(--font-display);
  font-size: 20px; font-weight: 500; color: var(--c-silver);
  cursor: pointer; padding: 0; position: relative;
}
.tab-btn.active { color: var(--c-black); }
.tab-btn.active::after {
  content: ''; position: absolute; bottom: -11px; left: 0;
  width: 100%; height: 2px; background: var(--c-black);
}

.view-panel { display: flex; flex-direction: column; gap: 24px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
.stat-card {
  background: var(--c-white); border: 1px solid var(--c-light-gray);
  border-radius: var(--radius-container); padding: 24px;
}
.stat-title { font-size: 13px; color: var(--c-stone); margin-bottom: 8px; }
.stat-val { font-family: var(--font-display); font-size: 28px; font-weight: 600; margin-bottom: 8px; }
.stat-trend { font-size: 12px; font-family: var(--font-mono); }
.stat-trend.up { color: #10b981; }
.stat-trend.down { color: #ef4444; }
.stat-trend.neutral { color: var(--c-stone); }

.panel-card {
  background: var(--c-white); border: 1px solid var(--c-light-gray);
  border-radius: var(--radius-container); padding: 24px;
}
.card-head { font-family: var(--font-display); font-size: 16px; font-weight: 500; margin-bottom: 20px; }
.placeholder-chart {
  height: 200px; background: var(--c-snow); border: 1px dashed var(--c-light-gray);
  border-radius: 8px; display: flex; align-items: center; justify-content: center;
  color: var(--c-silver); font-size: 13px;
}

.toolbar { margin-bottom: 16px; display: flex; align-items: center; }
.form-input {
  padding: 8px 16px; border: 1px solid var(--c-light-gray);
  border-radius: var(--radius-pill); font-size: 14px; outline: none; width: 100%;
}
.form-input:focus { border-color: var(--c-black); }
.form-textarea {
  padding: 12px 16px; border: 1px solid var(--c-light-gray);
  border-radius: 12px; font-size: 14px; outline: none; width: 100%;
  min-height: 100px; resize: vertical;
}
.form-textarea:focus { border-color: var(--c-black); }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-size: 13px; font-weight: 500; }

.data-table { width: 100%; border-collapse: collapse; text-align: left; }
.data-table th {
  padding: 12px 16px; font-size: 12px; color: var(--c-stone);
  border-bottom: 1px solid var(--c-light-gray); font-weight: 500;
}
.data-table td { padding: 16px; font-size: 14px; border-bottom: 1px solid var(--c-snow); }
.mono { font-family: var(--font-mono); color: var(--c-stone); font-size: 13px; }
.muted { color: var(--c-stone); font-size: 13px; }

.btn {
  padding: 6px 16px; background: var(--c-white); border: 1px solid var(--c-light-gray);
  border-radius: var(--radius-pill); font-size: 13px; cursor: pointer; color: var(--c-black);
}
.btn:hover { background: var(--c-snow); }
.btn.primary { background: var(--c-black); color: var(--c-white); border-color: var(--c-black); }
.btn.primary:hover { opacity: 0.8; }
.btn.danger { color: #ef4444; border-color: #fecaca; }
.btn.danger:hover { background: #fef2f2; }

.role-pill { padding: 4px 10px; border-radius: var(--radius-pill); font-size: 11px; }
.role-pill.admin { background: var(--c-black); color: var(--c-white); }
.role-pill.user { background: var(--c-snow); border: 1px solid var(--c-light-gray); }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.status-dot.active { background: #10b981; }
.status-dot.inactive { background: #ef4444; }

.action-btns { display: flex; gap: 8px; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: var(--c-white); border-radius: var(--radius-container);
  width: 90%; max-width: 700px; height: 80vh; display: flex; flex-direction: column;
}
.modal-head {
  padding: 20px 24px; border-bottom: 1px solid var(--c-light-gray);
  display: flex; justify-content: space-between; align-items: center;
}
.modal-title { font-family: var(--font-display); font-size: 18px; font-weight: 500; }
.modal-close { background: none; border: none; font-size: 16px; cursor: pointer; color: var(--c-stone); }
.modal-body { padding: 24px; flex: 1; overflow-y: auto; }

.chat-bubbles { display: flex; flex-direction: column; gap: 24px; }
.bubble-wrap { display: flex; gap: 12px; }
.bubble-wrap.user { flex-direction: row-reverse; }
.bubble-av {
  width: 32px; height: 32px; border-radius: 50%; background: var(--c-black); color: var(--c-white);
  display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600;
}
.bubble-av.user { background: var(--c-snow); color: var(--c-black); border: 1px solid var(--c-light-gray); }
.bubble-content { max-width: 80%; }
.bubble-text { padding: 12px 16px; font-size: 14px; line-height: 1.5; }
.bubble-text.user-text {
  background: var(--c-snow); border: 1px solid var(--c-light-gray);
  border-radius: 16px 16px 4px 16px;
}
.bubble-wrap.assistant .bubble-text { padding: 0; }

/* Markdown overrides */
.markdown-body { font-size: 14.5px; line-height: 1.6; }
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) { margin-top: 1.5em; margin-bottom: 0.5em; font-family: var(--font-display); }
.markdown-body :deep(p) { margin-bottom: 1em; }
.markdown-body :deep(ul) { padding-left: 20px; margin-bottom: 1em; }
.markdown-body :deep(li) { margin-bottom: 0.25em; }
</style>
