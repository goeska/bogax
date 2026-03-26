<script setup>
import { useLayout } from './composables/layout'
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'

const { containerClass, hideMobileMenu } = useLayout()
</script>

<template>
  <div class="layout-wrapper" :class="containerClass">
    <AppTopbar />
    <AppSidebar />
    <div class="layout-content-wrapper">
      <div class="layout-content">
        <RouterView />
      </div>
    </div>
    <div class="layout-mask" @click="hideMobileMenu" />
  </div>
</template>

