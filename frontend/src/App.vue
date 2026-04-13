<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const message = ref('招标信息智能问答系统')

const goHome = () => router.push('/')
const goAdmin = () => router.push('/admin')
</script>

<template>
  <el-container class="layout-container">
    <el-header class="header">
      <h2 @click="goHome" style="cursor:pointer">{{ message }}</h2>
      <div class="nav-links">
        <el-button type="primary" link @click="goHome">问答界面</el-button>
        <el-button type="primary" link @click="goAdmin">后台管理</el-button>
      </div>
    </el-header>
    <el-main class="main-content">
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f5f7fa;
}
.header {
  background-color: #ffffff;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.nav-links {
  display: flex;
  gap: 20px;
}
.main-content {
  padding: 20px;
  height: calc(100vh - 60px);
  box-sizing: border-box;
}
</style>
