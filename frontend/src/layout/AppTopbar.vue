<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLayout } from './composables/layout'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const { toggleMenu } = useLayout()

const title = computed(() => route.name?.toString().replaceAll('-', ' ') || 'BogaX')

function logout() {
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
      <h1 style="margin: 0; font-size: 1.05rem; font-weight: 700; text-transform: capitalize">{{ title }}</h1>
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

