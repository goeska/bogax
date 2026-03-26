<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import AppMenuItem from './AppMenuItem.vue'

const auth = useAuthStore()

const model = computed(() => [
  {
    label: 'Home',
    icon: 'pi pi-home',
    items: [{ label: 'Dashboard', icon: 'pi pi-chart-bar', to: '/' }],
  },
  {
    label: 'Master',
    icon: 'pi pi-database',
    items: [
      { label: 'Legal Entity Type', icon: 'pi pi-id-card', to: '/master/legal-entity-type' },
      { label: 'Partner', icon: 'pi pi-users', to: '/master/partner' },
      { label: 'CoA', icon: 'pi pi-book', to: '/master/coa' },
      { label: 'UOM', icon: 'pi pi-hashtag', to: '/master/uom' },
      { label: 'Tax', icon: 'pi pi-percentage', to: '/master/tax' },
      { label: 'Table', icon: 'pi pi-table', to: '/master/table' },
      { label: 'Product Category', icon: 'pi pi-tags', to: '/master/product-category' },
      { label: 'Product', icon: 'pi pi-box', to: '/master/product' },
    ],
  },
  {
    label: 'Sales',
    icon: 'pi pi-shopping-cart',
    items: [
      { label: 'SO List', icon: 'pi pi-list', to: '/sales/sales-order' },
      { label: 'SO Item List', icon: 'pi pi-list-check', to: '/sales/sales-order-line' },
      { label: 'Project', icon: 'pi pi-briefcase', to: '/sales/project' },
      { label: 'POS Retail', icon: 'pi pi-shopping-bag', to: '/sales/pos' },
    ],
  },
  {
    label: 'Purchase',
    icon: 'pi pi-shopping-bag',
    items: [
      { label: 'PO List', icon: 'pi pi-list', to: '/purchase/purchase-order' },
      { label: 'PO Item List', icon: 'pi pi-list-check', to: '/purchase/purchase-order-line' },
      { label: 'PO Form', icon: 'pi pi-file-edit', to: '/purchase/pos' },
      { label: 'Good Receipt Form', icon: 'pi pi-download', to: '/purchase/good-receipt' },
      { label: 'Good Receipt List', icon: 'pi pi-bars', to: '/purchase/good-receipt-list' },
    ],
  },
  {
    label: 'Main Config',
    icon: 'pi pi-cog',
    items: [
      { label: 'Business Type', icon: 'pi pi-building', to: '/main-config/business-type' },
      { label: 'Maintain Partner', icon: 'pi pi-wrench', to: '/main-config/maintain-customer' },
      ...(auth.user?.role === 'administrator'
        ? [{ label: 'Clear Sales', icon: 'pi pi-exclamation-triangle', to: '/main-config/clear-sales' }]
        : []),
    ],
  },
  {
    label: 'Admin',
    icon: 'pi pi-shield',
    items: [{ label: 'Users', icon: 'pi pi-user', to: '/admin/users' }],
  },
])
</script>

<template>
  <ul class="layout-menu">
    <AppMenuItem v-for="(item, index) in model" :key="item.label + index" :item="item" root />
  </ul>
</template>

