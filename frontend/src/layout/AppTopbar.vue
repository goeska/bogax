<script setup>
import { useRouter } from 'vue-router'
import { useLayout } from './composables/layout'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const { toggleMenu } = useLayout()

function logout() {
  const ok = window.confirm('Are you sure you want to log out?')
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
          <li>
            <span style="padding: 0.4rem 0.7rem; color: var(--text-color-secondary)">{{ auth.user?.email || 'User' }}</span>
          </li>
          <li>
            <a @click="logout"><i class="pi pi-sign-out" /></a>
          </li>
        </ul>
      </div>
    </div>
  </header>
</template>

