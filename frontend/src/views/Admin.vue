<script setup lang="ts">
import { ref, onMounted } from 'vue'
import request from '../api/request'
import { useRouter } from 'vue-router'

const router = useRouter()
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
  <div class="admin-layout">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="logo-area" @click="router.push('/')" style="cursor: pointer;">
          <svg class="llama-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
            <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/>
          </svg>
          <h1 class="brand-name">Bidding Admin</h1>
        </div>
        <nav class="nav-links">
          <a href="#" class="nav-link">Settings</a>
          <button class="nav-pill" @click="router.push('/')">Back to Chat</button>
        </nav>
      </div>
    </header>

    <!-- Main Admin Area -->
    <main class="main-container">
      <div class="admin-content">
        
        <div class="section-header">
          <h2 class="section-title">Query History</h2>
          <button class="action-pill" @click="fetchAllHistory">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="23 4 23 10 17 10"></polyline>
              <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
            </svg>
            Refresh
          </button>
        </div>

        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Session ID</th>
                <th>User ID</th>
                <th>Query Topic</th>
                <th>Created At</th>
                <th>Messages</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in historyData" :key="row.session_id">
                <td class="cell-mono">{{ row.session_id.substring(0, 8) }}...</td>
                <td>{{ row.user_id }}</td>
                <td class="cell-primary">{{ row.title }}</td>
                <td class="cell-muted">{{ new Date(row.created_at).toLocaleString() }}</td>
                <td>
                  <span class="badge">{{ row.msgCount }}</span>
                </td>
              </tr>
              <tr v-if="historyData.length === 0">
                <td colspan="5" class="empty-row">No history records found.</td>
              </tr>
            </tbody>
          </table>
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

.admin-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #fafafa; /* Slight off-white for admin background */
  color: #000000;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* --- Header --- */
.header {
  padding: 20px 32px;
  background-color: #ffffff;
  border-bottom: 1px solid #e5e5e5;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1280px;
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
  color: #737373;
  text-decoration: none;
  font-size: 16px;
  font-weight: 400;
}

.nav-link:hover {
  color: #000000;
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
}

.nav-pill:hover {
  background-color: #f5f5f5;
}

/* --- Main Area --- */
.main-container {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 48px 32px;
}

.admin-content {
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.section-title {
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 30px;
  font-weight: 500;
  margin: 0;
  color: #000000;
  letter-spacing: -0.02em;
}

.action-pill {
  background-color: #ffffff;
  color: #000000;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-pill:hover {
  background-color: #f5f5f5;
}

/* --- Table Styles --- */
.table-container {
  background-color: #ffffff;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  background-color: #fafafa;
  color: #737373;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e5e5;
}

.data-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #e5e5e5;
  font-size: 14px;
  color: #262626;
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.data-table tbody tr:hover {
  background-color: #fafafa;
}

.cell-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  color: #737373;
}

.cell-primary {
  font-weight: 500;
  color: #000000;
}

.cell-muted {
  color: #a3a3a3;
}

.badge {
  display: inline-block;
  padding: 2px 10px;
  background-color: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  color: #525252;
}

.empty-row {
  text-align: center;
  padding: 48px !important;
  color: #a3a3a3 !important;
}
</style>
