<script setup lang="ts">
import { ref } from 'vue'

const message = ref('Welcome to Bidding RAG System')
</script>

<template>
  <el-container class="layout-container">
    <el-header class="header">
      <h2>{{ message }}</h2>
    </el-header>
    <el-main>
      <el-card>
        <p>Frontend Base Architecture is ready!</p>
        <p>Tech Stack: Vue3 + TypeScript + Element Plus</p>
      </el-card>
    </el-main>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
  background-color: #f5f7fa;
}
.header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}
</style>
