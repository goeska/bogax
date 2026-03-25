import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { AUTH_STORAGE_KEY } from '../constants'

const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000/api')

function loadPersisted() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const persisted = loadPersisted()
  const accessToken = ref(persisted?.access ?? '')
  const refreshToken = ref(persisted?.refresh ?? '')
  const user = ref(persisted?.user ?? null)

  const isAuthenticated = computed(() => Boolean(accessToken.value))

  function persist() {
    localStorage.setItem(
      AUTH_STORAGE_KEY,
      JSON.stringify({
        access: accessToken.value,
        refresh: refreshToken.value,
        user: user.value,
      })
    )
  }

  async function login(email, password) {
    const { data } = await axios.post(`${baseURL}/auth/login/`, { email, password })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    user.value = data.user
    persist()
    return data
  }

  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem(AUTH_STORAGE_KEY)
  }

  return {
    user,
    isAuthenticated,
    login,
    logout,
  }
})
