<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import request from '../api/request'
import { ElMessage } from 'element-plus'

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
    ElMessage.error('发送失败，请重试')
    messages.value.pop() // remove user message on fail
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <el-card class="chat-card">
    <div class="chat-window">
      <div class="message-list" ref="scrollContainer">
        <div v-if="messages.length === 0" class="empty-state">
          欢迎使用招标智能问答系统，请在下方输入您的问题。
        </div>
        <div v-for="(msg, index) in messages" :key="index" :class="['message-item', msg.role]">
          <el-avatar v-if="msg.role === 'assistant'" :size="36" class="avatar">AI</el-avatar>
          <el-avatar v-else :size="36" class="avatar user-avatar">U</el-avatar>
          <div class="message-bubble">{{ msg.content }}</div>
        </div>
      </div>
      
      <div class="input-area">
        <el-input 
          v-model="query" 
          placeholder="请输入您的问题，例如：帮我查询北京科技有限公司的工商信息" 
          @keyup.enter="sendMessage"
          :disabled="loading"
        >
          <template #append>
            <el-button @click="sendMessage" :loading="loading" type="primary">发送</el-button>
          </template>
        </el-input>
      </div>
    </div>
  </el-card>
</template>

<style scoped>
.chat-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.chat-window {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 160px);
}
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}
.empty-state {
  text-align: center;
  color: #909399;
  margin-top: 50px;
}
.message-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.message-item.user {
  flex-direction: row-reverse;
}
.avatar {
  background-color: #409EFF;
}
.user-avatar {
  background-color: #67C23A;
}
.message-bubble {
  background-color: #f4f4f5;
  padding: 10px 15px;
  border-radius: 8px;
  max-width: 70%;
  line-height: 1.5;
}
.message-item.user .message-bubble {
  background-color: #e1f3d8;
}
.input-area {
  margin-top: 20px;
}
</style>
