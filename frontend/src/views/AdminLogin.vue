<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '../api/request'
import BrandMark from '../components/BrandMark.vue'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const submit = async () => {
  errorMsg.value = ''
  if (!username.value.trim() || !password.value) {
    errorMsg.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  try {
    const body = new URLSearchParams()
    body.set('username', username.value.trim())
    body.set('password', password.value)
    const res: any = await request.post('/auth/login', body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    if (!res?.user?.is_admin) {
      errorMsg.value = '该账号不是管理员'
      return
    }
    localStorage.setItem('admin_access_token', res.access_token)
    localStorage.setItem('admin_current_user', JSON.stringify(res.user))
    router.replace('/admin')
  } catch (e: any) {
    errorMsg.value = e?.response?.data?.message || e?.response?.data?.detail || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="card">
      <div class="brand">
        <BrandMark :size="34" />
        <div class="brand-text">
          <div class="brand-title">管理后台登录</div>
          <div class="brand-sub">招投标信息智能问答平台</div>
        </div>
      </div>

      <div class="form">
        <label class="label">管理员账号</label>
        <input class="input" v-model="username" placeholder="请输入用户名" autocomplete="username" />
        <label class="label">密码</label>
        <input class="input" v-model="password" type="password" placeholder="请输入密码" autocomplete="current-password" @keyup.enter="submit" />
        <div v-if="errorMsg" class="error">{{ errorMsg }}</div>
        <button class="btn-primary" :disabled="loading" @click="submit">
          {{ loading ? '登录中…' : '登录' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'SF Pro Rounded';
  src: local('SF Pro Rounded'), local('-apple-system');
  font-weight: 400 600;
}

.auth-page {
  height: 100vh;
  width: 100%;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  color: #000000;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.card {
  width: 100%;
  max-width: 520px;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  background: #ffffff;
  padding: 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}

.brand-title {
  font-family: 'SF Pro Rounded', ui-sans-serif, system-ui, sans-serif;
  font-size: 20px;
  font-weight: 500;
  letter-spacing: -0.02em;
}

.brand-sub {
  margin-top: 6px;
  font-size: 14px;
  color: #737373;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.label {
  font-size: 12px;
  color: #737373;
}

.input {
  width: 100%;
  border: 1px solid #e5e5e5;
  border-radius: 9999px;
  padding: 10px 16px;
  font-size: 16px;
  outline: none;
  background: #ffffff;
  color: #000000;
}

.input::placeholder {
  color: #a3a3a3;
}

.input:focus {
  border-color: #d4d4d4;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.5);
}

.error {
  font-size: 14px;
  color: #000000;
  background: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 12px;
  padding: 10px 12px;
}

.btn-primary {
  margin-top: 4px;
  border: 1px solid #000000;
  background: #000000;
  color: #ffffff;
  border-radius: 9999px;
  padding: 10px 24px;
  font-size: 16px;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>

