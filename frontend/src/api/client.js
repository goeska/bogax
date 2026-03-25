import axios from 'axios'
import { AUTH_STORAGE_KEY } from '../constants'

const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000/api')

function readAuth() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function writeAccessToken(access) {
  const auth = readAuth()
  if (!auth) return
  auth.access = access
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth))
}

export const api = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const auth = readAuth()
  if (auth?.access) {
    config.headers.Authorization = `Bearer ${auth.access}`
  }
  return config
})

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config
    const auth = readAuth()
    if (
      error.response?.status === 401 &&
      auth?.refresh &&
      !original._retry
    ) {
      original._retry = true
      try {
        const { data } = await axios.post(`${baseURL}/auth/refresh/`, {
          refresh: auth.refresh,
        })
        writeAccessToken(data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      } catch {
        localStorage.removeItem(AUTH_STORAGE_KEY)
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
