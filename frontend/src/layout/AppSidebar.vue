<script setup>
import AppMenu from './AppMenu.vue'
</script>

<template>
  <aside class="layout-sidebar">
    <div class="layout-sidebar-top">
      <a href="/" class="layout-sidebar-logo" aria-label="BogaX home">
        <span style="font-weight: 800; font-size: 1.1rem; letter-spacing: 0.02em">BogaX</span>
      </a>
    </div>
    <div class="layout-menu-container">
      <AppMenu />
    </div>
  </aside>
</template>

