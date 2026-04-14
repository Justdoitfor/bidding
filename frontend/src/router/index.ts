import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/Chat.vue'
import Admin from '../views/Admin.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import AdminLogin from '../views/AdminLogin.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLogin
    },
    {
      path: '/',
      name: 'chat',
      component: Chat
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin
    }
  ]
})

router.beforeEach((to) => {
  const isAdminRoute = to.path.startsWith('/admin')
  const isAdminLogin = to.path === '/admin/login'
  const isAuthRoute = to.path === '/login' || to.path === '/register'

  if (isAdminRoute) {
    const adminToken = localStorage.getItem('admin_access_token')
    const adminRaw = localStorage.getItem('admin_current_user')
    const adminUser = adminRaw ? JSON.parse(adminRaw) : null

    if (isAdminLogin) {
      if (adminToken && adminUser?.is_admin) return { path: '/admin' }
      return true
    }
    if (!adminToken || !adminUser?.is_admin) return { path: '/admin/login' }
    return true
  }

  const token = localStorage.getItem('access_token')
  const userRaw = localStorage.getItem('current_user')
  const user = userRaw ? JSON.parse(userRaw) : null

  if (isAuthRoute) {
    if (token) return { path: '/' }
    return true
  }

  if (!token) return { path: '/login' }
  return true
})

export default router
