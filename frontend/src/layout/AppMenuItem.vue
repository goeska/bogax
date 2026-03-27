<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useLayout } from './composables/layout'

const props = defineProps({
  item: { type: Object, required: true },
  root: { type: Boolean, default: false },
})

const route = useRoute()
const { layoutState } = useLayout()

const isRouteActive = computed(() => {
  if (!props.item.to) return false
  const pathMatches = route.path === props.item.to || route.path.startsWith(`${props.item.to}/`)
  if (!pathMatches) return false
  if (!props.item.query || typeof props.item.query !== 'object') return true
  return Object.entries(props.item.query).every(([key, value]) => String(route.query[key] ?? '') === String(value))
})

const hasChildren = computed(() => Array.isArray(props.item.items) && props.item.items.length > 0)
const expanded = ref(props.root ? subtreeHasActiveRoute(props.item) : true)
const linkTarget = computed(() => {
  if (!props.item.to) return null
  if (props.item.query && typeof props.item.query === 'object') {
    return { path: props.item.to, query: props.item.query }
  }
  return props.item.to
})

function subtreeHasActiveRoute(item) {
  if (!item) return false
  if (item.to && (route.path === item.to || route.path.startsWith(`${item.to}/`))) return true
  if (!Array.isArray(item.items)) return false
  return item.items.some((child) => subtreeHasActiveRoute(child))
}

const shouldShowChildren = computed(() => hasChildren.value && expanded.value)

function toggleChildren() {
  if (hasChildren.value) expanded.value = !expanded.value
}

function itemClick() {
  if (!hasChildren.value) {
    layoutState.overlayMenuActive = false
    layoutState.mobileMenuActive = false
  }
}
</script>

<template>
  <li :class="{ 'layout-root-menuitem': root, 'active-menuitem': isRouteActive }">
    <div
      v-if="root"
      class="layout-menuitem-root-text"
      role="button"
      tabindex="0"
      @click="toggleChildren"
      @keydown.enter.prevent="toggleChildren"
      @keydown.space.prevent="toggleChildren"
    >
      <span>{{ item.label }}</span>
      <i class="layout-menuitem-root-icon pi pi-fw" :class="shouldShowChildren ? 'pi-angle-up' : 'pi-angle-down'" />
    </div>

    <RouterLink
      v-if="item.to && !hasChildren"
      :to="linkTarget"
      :class="{ 'active-route': isRouteActive }"
      :aria-current="isRouteActive ? 'page' : undefined"
      @click="itemClick"
    >
      <i :class="item.icon" class="layout-menuitem-icon" />
      <span class="layout-menuitem-text">{{ item.label }}</span>
    </RouterLink>

    <a v-else href="#" @click.prevent="toggleChildren">
      <i :class="item.icon" class="layout-menuitem-icon" />
      <span class="layout-menuitem-text">{{ item.label }}</span>
      <i
        class="pi pi-fw layout-submenu-toggler"
        :class="shouldShowChildren ? 'pi-angle-up' : 'pi-angle-down'"
      />
    </a>

    <ul v-if="shouldShowChildren" :class="{ 'layout-root-submenulist': root }">
      <AppMenuItem v-for="child in item.items" :key="child.label + (child.to || '')" :item="child" />
    </ul>
  </li>
</template>

