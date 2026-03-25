<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

const open = ref(false)
const root = ref(null)

function close() {
  open.value = false
}

function toggle() {
  open.value = !open.value
}

function onDocClick(e) {
  if (!root.value?.contains(e.target)) close()
}

onMounted(() => document.addEventListener('click', onDocClick))
onUnmounted(() => document.removeEventListener('click', onDocClick))
</script>

<template>
  <div class="guest-shell">
    <header class="guest-topbar">
      <RouterLink to="/login" class="guest-brand">
        <span class="brand-mark">B</span>
        <span class="guest-brand-text">BogaX</span>
      </RouterLink>
      <div ref="root" class="account-wrap">
        <button
          type="button"
          class="account-trigger"
          :aria-expanded="open"
          aria-haspopup="true"
          @click.stop="toggle"
        >
          Account
          <span class="account-chevron" aria-hidden="true">{{ open ? '▾' : '▸' }}</span>
        </button>
        <div v-show="open" class="account-menu" role="menu">
          <button
            type="button"
            class="account-item account-item--current"
            role="menuitem"
            disabled
          >
            Log in
          </button>
          <button type="button" class="account-item" role="menuitem" disabled title="Sign in first">
            Log out
          </button>
        </div>
      </div>
    </header>
    <div class="guest-body">
      <RouterView />
    </div>
  </div>
</template>
