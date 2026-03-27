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
      { label: 'Product Category', icon: 'pi pi-tags', to: '/master/product-category' },
      { label: 'Product', icon: 'pi pi-box', to: '/master/product' },
      { label: 'UOM', icon: 'pi pi-hashtag', to: '/master/uom' },
      { label: 'Tax', icon: 'pi pi-percentage', to: '/master/tax' },
      { label: 'CoA', icon: 'pi pi-book', to: '/master/coa' },
      { label: 'Resto Table', icon: 'pi pi-table', to: '/master/table' },
    ],
  },
  {
    label: 'Sales Retail',
    icon: 'pi pi-shopping-cart',
    items: [
      { label: 'POS', icon: 'pi pi-shopping-bag', to: '/sales/pos' },
      { label: 'List', icon: 'pi pi-list', to: '/sales/sales-order', query: { order_type: 'retail' } },
      {
        label: 'Line List',
        icon: 'pi pi-list-check',
        to: '/sales/sales-order-line',
        query: { order_type: 'retail' },
      },
    ],
  },
  {
    label: 'Sales Non Retail',
    icon: 'pi pi-briefcase',
    items: [
      { label: 'Customer', icon: 'pi pi-users', to: '/master/partner' },
      { label: 'Project', icon: 'pi pi-briefcase', to: '/sales/project' },
      { label: 'SO Form', icon: 'pi pi-file-edit', to: '/sales/so-form' },
      {
        label: 'List',
        icon: 'pi pi-list',
        to: '/sales/sales-order',
        query: { order_type: 'non_retail' },
      },
      {
        label: 'Line List',
        icon: 'pi pi-list-check',
        to: '/sales/sales-order-line',
        query: { order_type: 'non_retail' },
      },
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

