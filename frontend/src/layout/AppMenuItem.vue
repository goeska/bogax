<script setup>
import { computed } from 'vue'
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
  return route.path === props.item.to || route.path.startsWith(`${props.item.to}/`)
})

const hasChildren = computed(() => Array.isArray(props.item.items) && props.item.items.length > 0)

function itemClick() {
  if (!hasChildren.value) {
    layoutState.overlayMenuActive = false
    layoutState.mobileMenuActive = false
  }
}
</script>

<template>
  <li :class="{ 'layout-root-menuitem': root, 'active-menuitem': isRouteActive }">
    <div v-if="root" class="layout-menuitem-root-text">
      <span>{{ item.label }}</span>
      <i class="layout-menuitem-root-icon pi pi-fw pi-ellipsis-h" />
    </div>

    <RouterLink
      v-if="item.to && !hasChildren"
      :to="item.to"
      class="active-route"
      :aria-current="isRouteActive ? 'page' : undefined"
      @click="itemClick"
    >
      <i :class="item.icon" class="layout-menuitem-icon" />
      <span class="layout-menuitem-text">{{ item.label }}</span>
    </RouterLink>

    <a v-else href="#" @click.prevent>
      <i :class="item.icon" class="layout-menuitem-icon" />
      <span class="layout-menuitem-text">{{ item.label }}</span>
      <i class="pi pi-fw pi-angle-down layout-submenu-toggler" />
    </a>

    <ul v-if="hasChildren" :class="{ 'layout-root-submenulist': root }">
      <AppMenuItem v-for="child in item.items" :key="child.label + (child.to || '')" :item="child" />
    </ul>
  </li>
</template>

