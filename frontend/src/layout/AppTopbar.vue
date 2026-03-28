<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useLayout } from './composables/layout'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { toggleMenu } = useLayout()
const userEmail = computed(() => auth.user?.email || 'User')
const todayLabel = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  }),
)

function logout() {
  const ok = window.confirm('Log out now?')
  if (!ok) return
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="layout-topbar">
    <div class="layout-topbar-start">
      <button type="button" class="layout-menu-button" aria-label="Toggle menu" @click="toggleMenu">
        <i class="pi pi-chevron-right" />
      </button>
      <a href="/" class="bogax-topbar-brand" aria-label="BogaX home">
        <span class="bogax-topbar-brand-title">BogaX</span>
        <span class="bogax-topbar-brand-sub">Reimagining the way you do business</span>
      </a>
    </div>
    <div class="layout-topbar-end">
      <div class="layout-topbar-actions-end">
        <ul class="layout-topbar-items">
          <li class="topbar-date-item">
            <span class="bogax-date-chip topbar-date-chip">
              <i class="pi pi-calendar" />
              <span>{{ todayLabel }}</span>
            </span>
          </li>
          <li>
            <span class="topbar-user-chip">
              <span class="topbar-user-email">{{ userEmail }}</span>
            </span>
          </li>
          <li>
            <button type="button" class="topbar-logout-btn" title="Logout" @click="logout">
              <i class="pi pi-sign-out" />
            </button>
          </li>
        </ul>
      </div>
    </div>
  </header>
</template>

