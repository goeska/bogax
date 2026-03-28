<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useLayout } from './composables/layout'
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'

const { containerClass, hideMobileMenu } = useLayout()
const route = useRoute()
const activeTitle = computed(() => route.name?.toString().replaceAll('-', ' ') || 'Dashboard')
const heroExcludedRoutes = new Set([
  'dashboard',
  'master-product',
  'sales-order',
  'sales-pos',
  'sales-so-form',
  'sales-do-form',
  'sales-project',
  'sales-order-line',
  'master-partner',
  'master-coa',
  'master-legal-entity-type',
  'master-tax',
  'master-table',
  'master-product-category',
  'master-uom',
  'purchase-order',
  'purchase-order-line',
  'purchase-good-receipt',
  'purchase-good-receipt-list',
  'admin-users',
  'main-config-business-type',
  'main-config-maintain-customer',
  'main-config-clear-sales',
])
const activeGroup = computed(() => {
  const path = route.path
  if (path.startsWith('/master/')) return { label: 'Master Data', icon: 'pi pi-database' }
  if (path.startsWith('/sales/')) return { label: 'Sales', icon: 'pi pi-shopping-cart' }
  if (path.startsWith('/purchase/')) return { label: 'Purchase', icon: 'pi pi-shopping-bag' }
  if (path.startsWith('/main-config/')) return { label: 'Main Config', icon: 'pi pi-cog' }
  if (path.startsWith('/admin/')) return { label: 'Admin', icon: 'pi pi-shield' }
  return { label: 'Home', icon: 'pi pi-home' }
})
const showWorkspaceHero = computed(() => !heroExcludedRoutes.has(String(route.name || '')))
const workspaceTitle = computed(() => {
  const raw = String(activeTitle.value || '').trim()
  if (!raw) return 'Workspace'
  return raw
    .split(' ')
    .filter(Boolean)
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ')
})
const workspaceSubtitle = computed(() => {
  const group = activeGroup.value.label
  if (group === 'Master Data')
    return 'Keep master data clean so the rest of the app just works.'
  if (group === 'Sales')
    return 'Quotes to cash - same flow every time.'
  if (group === 'Purchase')
    return 'POs, receipts, paperwork - without the chaos.'
  if (group === 'Main Config')
    return 'Flip the switches that match how you actually run things.'
  if (group === 'Admin') return 'Who gets in and what they can touch.'
  return 'Day-to-day ops, no fluff.'
})
</script>

<template>
  <div class="layout-wrapper" :class="containerClass">
    <AppTopbar />
    <div class="bogax-active-menu-strip">
      <div class="bogax-active-menu-strip-main">
        <span class="bogax-active-group-pill">
          <i class="pi" :class="activeGroup.icon" />
          <span>{{ activeGroup.label }}</span>
        </span>
        <i class="pi pi-angle-right bogax-active-menu-sep" />
        <span class="bogax-active-menu-title">{{ activeTitle }}</span>
      </div>
    </div>
    <AppSidebar />
    <div class="layout-content-wrapper">
      <div class="layout-content">
        <section v-if="showWorkspaceHero" class="card workspace-hero">
          <p class="workspace-kicker">{{ activeGroup.label }} Workspace</p>
          <div class="workspace-head-row">
            <h1 class="workspace-title">{{ workspaceTitle }}</h1>
            <span class="workspace-chip">ERP Professional View</span>
          </div>
          <p class="workspace-subtitle muted">{{ workspaceSubtitle }}</p>
        </section>
        <RouterView />
      </div>
    </div>
    <div class="layout-mask" @click="hideMobileMenu" />
  </div>
</template>

