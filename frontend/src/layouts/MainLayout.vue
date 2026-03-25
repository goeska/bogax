<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const accountOpen = ref(false)
const accountRoot = ref(null)
const navRoot = ref(null)
const openMenuTitle = ref(null)
/** Collapsible sections inside mega dropdown: key -> expanded (default true). */
const sectionExpanded = reactive({})

function closeAccount() {
  accountOpen.value = false
}

function toggleAccount() {
  accountOpen.value = !accountOpen.value
}

function signOutAndGoLogin() {
  auth.logout()
  router.push('/login')
  closeAccount()
}

function onDocumentClick(e) {
  if (!accountRoot.value?.contains(e.target)) closeAccount()
  if (!navRoot.value?.contains(e.target)) openMenuTitle.value = null
}

onMounted(() => document.addEventListener('click', onDocumentClick))
onUnmounted(() => document.removeEventListener('click', onDocumentClick))

watch(
  () => route.path,
  () => {
    closeAccount()
    openMenuTitle.value = null
  },
)

const navGroups = [
  {
    title: 'Home',
    items: [{ to: '/', label: 'Home', icon: '◇' }],
    sections: [],
  },
  {
    title: 'Master',
    items: [{ to: '/master/partner', label: 'Partner', icon: '○' }],
    sections: [
      {
        title: 'Reference',
        items: [
          { to: '/master/uom', label: 'UOM', icon: '⏚' },
          { to: '/master/tax', label: 'Tax', icon: '%' },
          { to: '/master/table', label: 'Table', icon: '▦' },
        ],
      },
      {
        title: 'Catalog',
        items: [
          { to: '/master/product-category', label: 'Prod. Category', icon: '▣' },
          { to: '/master/product', label: 'Product', icon: '▨' },
        ],
      },
    ],
  },
  {
    title: 'Sales',
    items: [
      { to: '/sales/sales-order', label: 'SO List', icon: '≡' },
      { to: '/sales/sales-order-line', label: 'SO Item List', icon: '⋯' },
      { to: '/sales/pos', label: 'POS', icon: '¤' },
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
          { to: '/purchase/purchase-order', label: 'PO List', icon: '≣' },
          { to: '/purchase/purchase-order-line', label: 'PO Item List', icon: '⋯' },
          { to: '/purchase/pos', label: 'PO Form', icon: '¤' },
        ],
      },
      {
        title: 'Receiving',
        items: [
          { to: '/purchase/good-receipt', label: 'Good Receipt Form', icon: '⬇' },
          { to: '/purchase/good-receipt-list', label: 'Good Receipt List', icon: '☰' },
        ],
      },
    ],
  },
  {
    title: 'Finance',
    items: [{ to: '/finance/payment', label: 'Payment', icon: '$' }],
    sections: [],
  },
  {
    title: 'Main Config',
    items: [
      {
        to: '/main-config/business-type',
        label: 'Business Type',
        icon: '⌂',
      },
      {
        to: '/main-config/maintain-customer',
        label: 'Maintain Partner',
        icon: '◎',
      },
    ],
    sections: [
      {
        title: 'Maintenance',
        items: [
          {
            to: '/main-config/clear-sales',
            label: 'Clear Sales',
            icon: '⚠',
            requiresRole: 'administrator',
          },
        ],
      },
    ],
  },
  {
    title: 'Admin',
    items: [{ to: '/admin/users', label: 'Users', icon: '👤' }],
    sections: [],
  },
]

/** Hide items marked with ``requiresRole`` when the user does not have that role. */
function navItemVisible(item) {
  if (item.requiresRole === 'administrator') {
    return auth.user?.role === 'administrator'
  }
  return true
}

function groupTopItems(group) {
  return (group.items || []).filter(navItemVisible).filter((i) => i.to != null)
}

function groupSections(group) {
  return group.sections || []
}

function sectionVisibleItems(section) {
  return (section.items || []).filter(navItemVisible).filter((i) => i.to != null)
}

function flatNavFromTitledGroup(group) {
  const out = [...groupTopItems(group)]
  for (const sec of groupSections(group)) {
    out.push(...sectionVisibleItems(sec))
  }
  return out
}

const titledNavGroups = computed(() => navGroups.filter((g) => g.title))

const flatNav = computed(() =>
  navGroups.flatMap((g) => flatNavFromTitledGroup(g)),
)

function sectionKey(groupTitle, sectionTitle, index) {
  return `${groupTitle}::${sectionTitle || index}`
}

function isSectionOpen(groupTitle, sectionTitle, index) {
  const key = sectionKey(groupTitle, sectionTitle, index)
  return sectionExpanded[key] !== false
}

function toggleSectionOpen(groupTitle, sectionTitle, index) {
  const key = sectionKey(groupTitle, sectionTitle, index)
  const open = isSectionOpen(groupTitle, sectionTitle, index)
  sectionExpanded[key] = !open
}

function toggleMegaMenu(title) {
  openMenuTitle.value = openMenuTitle.value === title ? null : title
}

function pathMatchesItem(path, item) {
  if (!item.to) return false
  return path === item.to || (item.to !== '/' && path.startsWith(`${item.to}/`))
}

function groupIsActive(group) {
  const path = route.path
  if (groupTopItems(group).some((i) => pathMatchesItem(path, i))) return true
  for (const sec of groupSections(group)) {
    if (sectionVisibleItems(sec).some((i) => pathMatchesItem(path, i))) return true
  }
  return false
}

const title = computed(() => {
  const path = route.path
  const m = flatNav.value.find(
    (n) => path === n.to || (n.to !== '/' && path.startsWith(`${n.to}/`)),
  )
  return m?.label ?? 'BogaX'
})
</script>

<template>
  <div class="shell shell--topnav">
    <header class="app-header" role="banner">
      <div class="app-header-top">
        <RouterLink to="/" class="brand-inline brand-inline--header">
          <span class="brand-mark">B</span>
          <strong class="brand-name-header">BogaX</strong>
          <span class="muted small brand-tagline brand-tagline--header">
            Reimagining the way you do business
          </span>
        </RouterLink>
        <div class="app-header-right">
          <span class="app-header-credit">Crafted by Goeska</span>
          <div v-if="auth.user?.email" class="user-line user-line--header">
            <span class="dot" />
            <span class="truncate">{{ auth.user.email }}</span>
          </div>
          <div ref="accountRoot" class="account-wrap">
            <button
              type="button"
              class="account-trigger account-trigger--header"
              :aria-expanded="accountOpen"
              aria-haspopup="true"
              @click.stop="toggleAccount"
            >
              Account
              <span class="account-chevron" aria-hidden="true">{{
                accountOpen ? '▾' : '▸'
              }}</span>
            </button>
            <div v-show="accountOpen" class="account-menu" role="menu">
              <div v-if="auth.user?.email" class="account-menu-head muted">
                {{ auth.user.email }}
              </div>
              <button
                type="button"
                class="account-item"
                role="menuitem"
                @click="signOutAndGoLogin"
              >
                Log in
              </button>
              <button
                type="button"
                class="account-item account-item--danger"
                role="menuitem"
                @click="signOutAndGoLogin"
              >
                Log out
              </button>
            </div>
          </div>
        </div>
      </div>
      <nav
        ref="navRoot"
        class="app-nav app-nav--mega"
        aria-label="Main navigation"
      >
        <div class="app-nav-bar">
          <div
            v-for="group in titledNavGroups"
            :key="group.title"
            class="nav-megamenu-item"
          >
            <button
              type="button"
              class="nav-mega-trigger"
              :class="{
                'nav-mega-trigger--active': groupIsActive(group),
                'nav-mega-trigger--open': openMenuTitle === group.title,
              }"
              :aria-expanded="openMenuTitle === group.title"
              aria-haspopup="true"
              @click.stop="toggleMegaMenu(group.title)"
            >
              {{ group.title }}
              <span class="nav-mega-chevron" aria-hidden="true">▾</span>
            </button>
            <div
              v-show="openMenuTitle === group.title"
              class="nav-mega-panel"
              role="menu"
            >
              <RouterLink
                v-for="item in groupTopItems(group)"
                :key="item.to"
                :to="item.to"
                class="nav-dd-link"
                active-class="nav-dd-link--active"
                :end="item.to === '/'"
                role="menuitem"
              >
                <span class="nav-ico nav-ico--dd">{{ item.icon }}</span>
                {{ item.label }}
              </RouterLink>
              <template
                v-for="(sec, si) in groupSections(group)"
                :key="sec.title + String(si)"
              >
                <div
                  v-if="sectionVisibleItems(sec).length"
                  class="nav-dd-section"
                >
                  <button
                    type="button"
                    class="nav-dd-section-toggle"
                    :aria-expanded="isSectionOpen(group.title, sec.title, si)"
                    @click.stop="
                      toggleSectionOpen(group.title, sec.title, si)
                    "
                  >
                    <span class="nav-dd-section-chevron" aria-hidden="true">{{
                      isSectionOpen(group.title, sec.title, si) ? '▼' : '▶'
                    }}</span>
                    <span class="nav-dd-section-title">{{ sec.title }}</span>
                  </button>
                  <div
                    v-show="isSectionOpen(group.title, sec.title, si)"
                    class="nav-dd-section-items"
                  >
                    <RouterLink
                      v-for="item in sectionVisibleItems(sec)"
                      :key="item.to"
                      :to="item.to"
                      class="nav-dd-link nav-dd-link--indent"
                      active-class="nav-dd-link--active"
                      :end="item.to === '/'"
                      role="menuitem"
                    >
                      <span class="nav-ico nav-ico--dd">{{ item.icon }}</span>
                      {{ item.label }}
                    </RouterLink>
                  </div>
                </div>
              </template>
            </div>
          </div>
        </div>
      </nav>
    </header>
    <div class="main">
      <header class="topbar topbar--page">
        <h1>{{ title }}</h1>
      </header>
      <main class="content">
        <RouterView />
      </main>
    </div>
  </div>
</template>
