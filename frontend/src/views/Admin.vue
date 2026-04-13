<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../api/request'

const historyData = ref([])

// Fetch History
const fetchAllHistory = async () => {
  try {
    const res: any = await request.get('/chat/admin/history')
    historyData.value = res.map((session: any) => {
      return {
        session_id: session.session_id,
        user_id: session.user_id,
        title: session.title,
        created_at: session.created_at,
        msgCount: session.messages.length
      }
    })
  } catch (error) {
    console.error('Failed to load history', error)
  }
}

onMounted(() => {
  fetchAllHistory()
})

</script>

<template>
  <el-container class="admin-layout">
    <el-header class="admin-header">
      <h2>后台管理中心</h2>
    </el-header>
    <el-main class="admin-main">
      <el-card class="admin-card">
        <template #header>
          <div class="card-header">
            <span>问答历史记录</span>
            <el-button type="primary" size="small" @click="fetchAllHistory">刷新记录</el-button>
          </div>
        </template>
        
        <el-table :data="historyData" border style="width: 100%" height="calc(100vh - 200px)">
          <el-table-column prop="session_id" label="会话ID" width="300" />
          <el-table-column prop="user_id" label="用户ID" width="150" />
          <el-table-column prop="title" label="提问主题" />
          <el-table-column prop="created_at" label="创建时间" width="200" />
          <el-table-column prop="msgCount" label="消息数" width="100" />
        </el-table>
      </el-card>
    </el-main>
  </el-container>
</template>

<style scoped>
.admin-layout {
  height: 100vh;
  background-color: #f0f2f5;
}
.admin-header {
  background-color: #304156;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
.admin-main {
  padding: 20px;
}
.admin-card {
  height: 100%;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
