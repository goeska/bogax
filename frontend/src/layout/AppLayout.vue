<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useLayout } from './composables/layout'
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'

const { containerClass, hideMobileMenu } = useLayout()
const route = useRoute()
const activeTitle = computed(() => route.name?.toString().replaceAll('-', ' ') || 'Dashboard')
const activeGroup = computed(() => {
  const path = route.path
  if (path.startsWith('/master/')) return { label: 'Master', icon: 'pi pi-database' }
  if (path.startsWith('/sales/')) return { label: 'Sales', icon: 'pi pi-shopping-cart' }
  if (path.startsWith('/purchase/')) return { label: 'Purchase', icon: 'pi pi-shopping-bag' }
  if (path.startsWith('/main-config/')) return { label: 'Main Config', icon: 'pi pi-cog' }
  if (path.startsWith('/admin/')) return { label: 'Admin', icon: 'pi pi-shield' }
  return { label: 'Home', icon: 'pi pi-home' }
})
</script>

<template>
  <div class="layout-wrapper" :class="containerClass">
    <AppTopbar />
    <div class="bogax-active-menu-strip">
      <span class="bogax-active-group-pill">
        <i class="pi" :class="activeGroup.icon" />
        <span>{{ activeGroup.label }}</span>
      </span>
      <i class="pi pi-angle-right bogax-active-menu-sep" />
      <span class="bogax-active-menu-title">{{ activeTitle }}</span>
    </div>
    <AppSidebar />
    <div class="layout-content-wrapper">
      <div class="layout-content">
        <RouterView />
      </div>
    </div>
    <div class="layout-mask" @click="hideMobileMenu" />
  </div>
</template>

