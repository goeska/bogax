<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const accountOpen = ref(false)
const sidebarCollapsed = ref(false)
const openGroups = ref(new Set(['Home', 'Master', 'Sales']))
const SIDEBAR_COLLAPSED_KEY = 'bogax:sidebar-collapsed'

function signOutAndGoLogin() {
  auth.logout()
  router.push('/login')
}

const navGroups = [
  {
    title: 'Home',
    items: [{ to: '/', label: 'Home', icon: 'pi pi-home' }],
    sections: [],
  },
  {
    title: 'Master',
    items: [
      { to: '/master/legal-entity-type', label: 'Legal Entity Type', icon: 'pi pi-id-card' },
      { to: '/master/partner', label: 'Partner', icon: 'pi pi-users' },
    ],
    sections: [
      {
        title: 'Reference',
        items: [
          { to: '/master/coa', label: 'CoA', icon: 'pi pi-book' },
          { to: '/master/uom', label: 'UOM', icon: 'pi pi-hashtag' },
          { to: '/master/tax', label: 'Tax', icon: 'pi pi-percentage' },
          { to: '/master/table', label: 'Table', icon: 'pi pi-table' },
        ],
      },
      {
        title: 'Catalog',
        items: [
          { to: '/master/product-category', label: 'Prod. Category', icon: 'pi pi-tags' },
          { to: '/master/product', label: 'Product', icon: 'pi pi-box' },
        ],
      },
    ],
  },
  {
    title: 'Sales',
    items: [
      { to: '/sales/sales-order', label: 'SO List', icon: 'pi pi-list' },
      { to: '/sales/sales-order-line', label: 'SO Item List', icon: 'pi pi-list-check' },
      { to: '/sales/project', label: 'Project', icon: 'pi pi-briefcase' },
      { to: '/sales/pos', label: 'POS Retail', icon: 'pi pi-shopping-cart' },
    ],
    sections: [],
  },
  {
    title: 'Purchase',
    items: [],
    sections: [
      {
        title: 'Orders',
        items: [
          { to: '/purchase/purchase-order', label: 'PO List', icon: 'pi pi-list' },
          { to: '/purchase/purchase-order-line', label: 'PO Item List', icon: 'pi pi-list-check' },
          { to: '/purchase/pos', label: 'PO Form', icon: 'pi pi-file-edit' },
        ],
      },
      {
        title: 'Receiving',
        items: [
          { to: '/purchase/good-receipt', label: 'Good Receipt Form', icon: 'pi pi-download' },
          { to: '/purchase/good-receipt-list', label: 'Good Receipt List', icon: 'pi pi-bars' },
        ],
      },
    ],
  },
  {
    title: 'Main Config',
    items: [
      { to: '/main-config/business-type', label: 'Business Type', icon: 'pi pi-building' },
      { to: '/main-config/maintain-customer', label: 'Maintain Partner', icon: 'pi pi-cog' },
      { to: '/main-config/clear-sales', label: 'Clear Sales', icon: 'pi pi-exclamation-triangle' },
    ],
    sections: [],
  },
  {
    title: 'Admin',
    items: [{ to: '/admin/users', label: 'Users', icon: 'pi pi-user' }],
    sections: [],
  },
]

function itemVisible(item) {
  if (item.to === '/main-config/clear-sales') return auth.user?.role === 'administrator'
  return true
}

function groupIsOpen(title) {
  return openGroups.value.has(title)
}

function toggleGroup(title) {
  const next = new Set(openGroups.value)
  if (next.has(title)) next.delete(title)
  else next.add(title)
  openGroups.value = next
}

function allItems(group) {
  const top = (group.items || []).filter(itemVisible)
  const sec = (group.sections || []).flatMap((s) => (s.items || []).filter(itemVisible))
  return [...top, ...sec]
}

function isActive(to) {
  return route.path === to || (to !== '/' && route.path.startsWith(`${to}/`))
}

onMounted(() => {
  const saved = localStorage.getItem(SIDEBAR_COLLAPSED_KEY)
  if (saved === '1') sidebarCollapsed.value = true
})

watch(sidebarCollapsed, (collapsed) => {
  localStorage.setItem(SIDEBAR_COLLAPSED_KEY, collapsed ? '1' : '0')
})

const pageTitle = computed(() => {
  for (const g of navGroups) {
    for (const i of allItems(g)) if (isActive(i.to)) return i.label
  }
  return 'Dashboard'
})

const activeGroupTitle = computed(() => {
  for (const g of navGroups) {
    if (allItems(g).some((i) => isActive(i.to))) return g.title
  }
  return 'Home'
})

const breadcrumbs = computed(() => [
  { label: 'Home', to: '/' },
  ...(activeGroupTitle.value !== 'Home' ? [{ label: activeGroupTitle.value }] : []),
  { label: pageTitle.value },
])
</script>

<template>
  <div class="hyb-shell" :class="{ 'hyb-shell--collapsed': sidebarCollapsed }">
    <aside class="hyb-sidebar">
      <div class="hyb-brand">
        <div class="hyb-brand-mark">B</div>
        <div class="hyb-brand-text">
          <div class="hyb-brand-title">BogaX</div>
          <div class="hyb-brand-sub">Reimagining the way you do business</div>
        </div>
      </div>

      <nav class="hyb-nav">
        <div v-for="group in navGroups" :key="group.title" class="hyb-group">
          <button
            class="hyb-group-head"
            type="button"
            :aria-label="sidebarCollapsed ? group.title : undefined"
            :aria-expanded="groupIsOpen(group.title)"
            @click="toggleGroup(group.title)"
          >
            <span>{{ group.title }}</span>
            <i class="pi" :class="groupIsOpen(group.title) ? 'pi-chevron-down' : 'pi-chevron-right'" />
            <span v-if="sidebarCollapsed" class="hyb-tooltip">{{ group.title }}</span>
          </button>
          <div v-show="groupIsOpen(group.title)" class="hyb-group-items">
            <RouterLink
              v-for="item in allItems(group)"
              :key="item.to"
              :to="item.to"
              class="hyb-link"
              :class="{ 'is-active': isActive(item.to) }"
              :aria-label="sidebarCollapsed ? item.label : undefined"
              :aria-current="isActive(item.to) ? 'page' : undefined"
            >
              <i class="pi" :class="item.icon" />
              <span>{{ item.label }}</span>
              <span v-if="sidebarCollapsed" class="hyb-tooltip">{{ item.label }}</span>
            </RouterLink>
          </div>
        </div>
      </nav>
    </aside>

    <div class="hyb-main">
      <header class="hyb-topbar">
        <div class="hyb-topbar-left">
          <div class="hyb-topbar-actions">
            <button
              type="button"
              class="hyb-collapse-btn"
              :title="sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
              @click="sidebarCollapsed = !sidebarCollapsed"
            >
              <i class="pi" :class="sidebarCollapsed ? 'pi-angle-double-right' : 'pi-angle-double-left'" />
            </button>
          </div>
          <nav class="hyb-breadcrumb" aria-label="Breadcrumb">
            <span v-for="(bc, idx) in breadcrumbs" :key="`${bc.label}-${idx}`" class="hyb-bc-item">
              <RouterLink v-if="bc.to && idx < breadcrumbs.length - 1" :to="bc.to">{{ bc.label }}</RouterLink>
              <span v-else>{{ bc.label }}</span>
              <i v-if="idx < breadcrumbs.length - 1" class="pi pi-angle-right hyb-bc-sep" />
            </span>
          </nav>
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="hyb-topbar-right">
          <span class="hyb-user">{{ auth.user?.email || 'User' }}</span>
          <div class="hyb-account">
            <button class="hyb-account-btn" @click="accountOpen = !accountOpen">Account</button>
            <div v-if="accountOpen" class="hyb-account-menu">
              <button @click="signOutAndGoLogin">Log out</button>
            </div>
          </div>
        </div>
      </header>
      <main class="hyb-content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

