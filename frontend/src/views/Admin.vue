<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import BrandMark from '../components/BrandMark.vue'

const route = useRoute()
const currentUser = ref(JSON.parse(localStorage.getItem('admin_current_user') || '{}'))

// View Meta mapping based on route name
const viewMeta: Record<string, { title: string, sub: string }> = {
  'admin-dashboard': { title: '仪表盘', sub: '平台运行状态总览' },
  'knowledge-base': { title: '知识库管理', sub: '向量索引与文档知识库' },
  'documents': { title: '文档处理', sub: '上传与管理业务数据' }
}

const pageTitle = computed(() => viewMeta[route.name as string]?.title || '管理中心')
const pageSub = computed(() => viewMeta[route.name as string]?.sub || '系统管理与配置')

const logout = () => {
  localStorage.removeItem('admin_access_token')
  localStorage.removeItem('admin_current_user')
  window.location.href = '/admin/login'
}
</script>

<template>
  <div class="admin-app">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="brand">
        <BrandMark :size="24" class="logo-mark" />
        <span class="logo-name">智链管理平台</span>
      </div>
      <nav class="nav-menu">
        <div class="nav-section">总览</div>
        <router-link to="/admin" :class="['nav-item', { active: route.name === 'admin-dashboard' }]">
          <span class="nav-icon">◱</span> 仪表盘
        </router-link>
        
        <div class="nav-section" style="margin-top:24px">知识与数据</div>
        <router-link to="/admin/kb" :class="['nav-item', { active: route.name === 'knowledge-base' || route.name === 'documents' }]">
          <span class="nav-icon">📚</span> 知识库管理
        </router-link>
      </nav>
      <div class="user-footer">
        <div class="user-avatar">{{ (currentUser.username || 'A').charAt(0).toUpperCase() }}</div>
        <div class="user-info">
          <div class="u-name">{{ currentUser.username || 'Admin' }}</div>
          <div class="u-role">超级管理员</div>
        </div>
        <button class="logout-btn" @click="logout" title="退出">🚪</button>
      </div>
    </aside>

    <!-- Main Layout -->
    <div class="main-content">
      <!-- Topbar -->
      <header class="topbar">
        <div>
          <div class="page-title">{{ pageTitle }}</div>
          <div class="page-sub">{{ pageSub }}</div>
        </div>
        <div class="topbar-right">
          <div class="status-indicator"><span class="dot"></span>服务正常</div>
        </div>
      </header>

      <!-- Scrollable View Area -->
      <main class="view-area">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-app {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--c-snow);
  color: var(--c-black);
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: var(--c-white);
  border-right: 1px solid var(--c-light-gray);
  display: flex;
  flex-direction: column;
}
.brand {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 12px;
  border-bottom: 1px solid var(--c-light-gray);
}
.logo-name {
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
}
.nav-menu {
  flex: 1;
  padding: 24px 16px;
  overflow-y: auto;
}
.nav-section {
  font-size: 11px;
  color: var(--c-stone);
  margin-bottom: 8px;
  padding-left: 12px;
  font-family: var(--font-mono);
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  color: var(--c-mid-gray);
  border-radius: var(--radius-pill);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  margin-bottom: 4px;
  text-decoration: none;
}
.nav-item:hover {
  background: var(--c-snow);
  color: var(--c-black);
}
.nav-item.active {
  background: var(--c-black);
  color: var(--c-white);
}
.user-footer {
  padding: 16px;
  border-top: 1px solid var(--c-light-gray);
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--c-snow);
  border: 1px solid var(--c-light-gray);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}
.user-info {
  flex: 1;
  overflow: hidden;
}
.u-name {
  font-size: 13px;
  font-weight: 500;
}
.u-role {
  font-size: 11px;
  color: var(--c-stone);
}
.logout-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
}

/* Main */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.topbar {
  height: 64px;
  background: var(--c-white);
  border-bottom: 1px solid var(--c-light-gray);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
}
.page-title {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 600;
}
.page-sub {
  font-size: 12px;
  color: var(--c-stone);
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--c-mid-gray);
}
.status-indicator .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.view-area {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
}
</style>
