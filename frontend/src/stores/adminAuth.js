import { defineStore } from 'pinia'
import adminApi from '@/utils/adminApi'

export const useAdminAuthStore = defineStore('adminAuth', {
  state: () => ({ token: localStorage.getItem('ADMIN_TOKEN') || '', refreshToken: localStorage.getItem('ADMIN_REFRESH_TOKEN') || '', user: null, loading: false }),
  getters: { isAuthed: (s) => !!s.token },
  actions: {
    async loadUser() {
      if (!this.token) return
      try {
        const res = await adminApi.get('/auth/me')
        if (res.data?.user) {
          this.user = res.data.user
        }
      } catch (error) {
        // Token可能已过期，清除状态
        this.token = ''
        this.refreshToken = ''
        this.user = null
        try {
          localStorage.removeItem('ADMIN_TOKEN')
          localStorage.removeItem('ADMIN_REFRESH_TOKEN')
        } catch {}
      }
    },
    async login(username, password) {
      this.loading = true
      try {
        const res = await adminApi.post('/auth/login', { username, password })
        const { token, refresh_token, user } = res.data || {}
        if (token) {
          this.token = token
          this.refreshToken = refresh_token || ''
          this.user = user || { username, permissions: [] }
          localStorage.setItem('ADMIN_TOKEN', token)
          if (this.refreshToken) localStorage.setItem('ADMIN_REFRESH_TOKEN', this.refreshToken)
          // 如果没有返回用户信息，尝试加载
          if (!user) {
            await this.loadUser()
          }
          return true
        }
        return false
      } catch (e) {
        return false
      } finally {
        this.loading = false
      }
    },
    async logout() {
      try {
        await adminApi.post('/auth/logout', { refresh_token: this.refreshToken })
      } catch {}
      this.token = ''
      this.refreshToken = ''
      this.user = null
      try { localStorage.removeItem('ADMIN_TOKEN'); localStorage.removeItem('ADMIN_REFRESH_TOKEN') } catch {}
    },
    hasPerm(code) {
      const perms = this.user?.permissions || []
      return perms.includes(code)
    }
  }
})
