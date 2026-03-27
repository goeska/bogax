import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    component: () => import('../layouts/GuestLayout.vue'),
    meta: { guest: true },
    children: [
      {
        path: '',
        name: 'login',
        component: () => import('../views/LoginView.vue'),
      },
    ],
  },
  {
    path: '/',
    component: () => import('../layout/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'dashboard', component: () => import('../views/DashboardView.vue') },
      {
        path: 'master/coa',
        name: 'master-coa',
        component: () => import('../views/master/CoaView.vue'),
      },
      {
        path: 'master/uom',
        name: 'master-uom',
        component: () => import('../views/master/UomView.vue'),
      },
      {
        path: 'master/partner',
        name: 'master-partner',
        component: () => import('../views/master/PartnerView.vue'),
      },
      {
        path: 'master/legal-entity-type',
        name: 'master-legal-entity-type',
        component: () => import('../views/master/LegalEntityTypeView.vue'),
      },
      {
        path: 'master/tax',
        name: 'master-tax',
        component: () => import('../views/master/TaxView.vue'),
      },
      {
        path: 'master/table',
        name: 'master-table',
        component: () => import('../views/master/TableView.vue'),
      },
      {
        path: 'master/product-category',
        name: 'master-product-category',
        component: () => import('../views/master/ProductCategoryView.vue'),
      },
      {
        path: 'master/product',
        name: 'master-product',
        component: () => import('../views/master/ProductView.vue'),
      },
      {
        path: 'sales/sales-order',
        name: 'sales-order',
        component: () => import('../views/sales/SalesOrderView.vue'),
      },
      {
        path: 'sales/sales-order-line',
        name: 'sales-order-line',
        component: () => import('../views/sales/SalesOrderLineView.vue'),
      },
      {
        path: 'sales/pos',
        name: 'sales-pos',
        component: () => import('../views/sales/PosView.vue'),
      },
      {
        path: 'sales/so-form',
        name: 'sales-so-form',
        component: () => import('../views/sales/PosView.vue'),
      },
      {
        path: 'sales/project',
        name: 'sales-project',
        component: () => import('../views/sales/ProjectView.vue'),
      },
      {
        path: 'purchase/purchase-order',
        name: 'purchase-order',
        component: () => import('../views/purchase/PurchaseOrderView.vue'),
      },
      {
        path: 'purchase/pos',
        name: 'purchase-pos',
        component: () => import('../views/purchase/PurchasePosView.vue'),
      },
      {
        path: 'purchase/purchase-order-line',
        name: 'purchase-order-line',
        component: () => import('../views/purchase/PurchaseOrderLineView.vue'),
      },
      {
        path: 'purchase/good-receipt',
        name: 'purchase-good-receipt',
        component: () => import('../views/purchase/GoodReceiptView.vue'),
      },
      {
        path: 'purchase/good-receipt-list',
        name: 'purchase-good-receipt-list',
        component: () => import('../views/purchase/GoodReceiptListView.vue'),
      },
      {
        path: 'main-config/business-type',
        name: 'main-config-business-type',
        component: () => import('../views/mainconfig/BusinessTypeView.vue'),
      },
      {
        path: 'main-config/maintain-customer',
        name: 'main-config-maintain-customer',
        component: () => import('../views/mainconfig/MaintainPartnerView.vue'),
      },
      {
        path: 'main-config/clear-sales',
        name: 'main-config-clear-sales',
        component: () => import('../views/mainconfig/ClearSalesView.vue'),
      },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: () => import('../views/admin/UsersView.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guest && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
  if (to.name === 'main-config-clear-sales' && auth.user?.role !== 'administrator') {
    return { name: 'dashboard' }
  }
  return true
})

export default router
