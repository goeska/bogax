import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHistory } from 'vue-router';

const routes = [
    {
        path: '/',
        component: AppLayout,
        children: [
            {
                path: '/dashboards/analytics',
                alias: '/',
                name: 'dashboard-analytics',
                exact: true,
                component: () => import('@/views/dashboards/DashboardAnalytics.vue'),
                meta: {
                    breadcrumb: [{ label: 'Analytics Dashboard' }]
                }
            },
            {
                path: '/dashboards/sales',
                name: 'dashboard-sales',
                exact: true,
                component: () => import('@/views/dashboards/Dashboard.vue'),
                meta: {
                    breadcrumb: [{ label: 'Sales Dashboard' }]
                }
            },
            {
                path: '/dashboards/sass',
                name: 'dashboard-sass',
                exact: true,
                component: () => import('@/views/dashboards/DashboardSaas.vue'),
                meta: {
                    breadcrumb: [{ label: 'SaaS Dashboard' }]
                }
            },
            {
                path: '/apps/cms/list',
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'CMS', item: 'List' }]
                },
                component: () => import('@/views/apps/cms/List.vue')
            },
            {
                path: '/apps/cms/detail',
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'CMS', item: 'Detail' }]
                },
                component: () => import('@/views/apps/cms/Detail.vue')
            },
            {
                path: '/apps/cms/detail2',
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'CMS', item: 'Detail-2' }]
                },
                component: () => import('@/views/apps/cms/Detail2.vue')
            },
            {
                path: '/apps/cms/edit',
                name: 'cms-edit',
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'CMS', item: 'Edit' }]
                },
                component: () => import('@/views/apps/cms/Edit.vue')
            },
            {
                path: '/apps/files',
                name: 'files',
                component: () => import('@/views/apps/Files.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'Files' }]
                }
            },
            {
                path: '/apps/chat',
                name: 'chat',
                component: () => import('@/views/apps/chat/Index.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'Chat' }]
                }
            },
            {
                path: '/apps/tasklist',
                name: 'tasklist',
                component: () => import('@/views/apps/tasklist/Index.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Apps', label: 'Task List' }]
                }
            },
            {
                path: '/apps/mail',
                component: () => import('@/views/apps/mail/Index.vue'),
                children: [
                    {
                        path: '',
                        redirect: '/apps/mail/inbox'
                    },
                    {
                        path: 'inbox',
                        name: 'mail-inbox',
                        component: () => import('@/views/apps/mail/Inbox.vue'),
                        meta: {
                            breadcrumb: [{ parent: 'Apps', label: 'Mail', item: 'Inbox' }]
                        }
                    },
                    {
                        path: 'detail/:id',
                        name: 'mail-detail',
                        component: () => import('@/views/apps/mail/Detail.vue'),
                        meta: {
                            breadcrumb: [{ parent: 'Apps', label: 'Mail', item: 'Detail' }]
                        }
                    }
                ]
            },
            {
                path: '/uikit/formlayout',
                name: 'formlayout',

                component: () => import('@/views/uikit/FormLayoutDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Form Layout' }]
                }
            },
            {
                path: '/uikit/input',
                name: 'input',
                component: () => import('@/views/uikit/InputDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Input' }]
                }
            },
            {
                path: '/uikit/button',
                name: 'button',
                component: () => import('@/views/uikit/ButtonDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Button' }]
                }
            },
            {
                path: '/uikit/table',
                name: 'table',
                component: () => import('@/views/uikit/TableDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Table' }]
                }
            },
            {
                path: '/uikit/list',
                name: 'list',
                component: () => import('@/views/uikit/ListDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'List' }]
                }
            },
            {
                path: '/uikit/tree',
                name: 'tree',
                component: () => import('@/views/uikit/TreeDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Tree' }]
                }
            },
            {
                path: '/uikit/panel',
                name: 'panel',
                component: () => import('@/views/uikit/PanelsDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Panel' }]
                }
            },
            {
                path: '/uikit/overlay',
                name: 'overlay',
                component: () => import('@/views/uikit/OverlayDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Overlay' }]
                }
            },
            {
                path: '/uikit/media',
                name: 'media',
                component: () => import('@/views/uikit/MediaDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Media' }]
                }
            },
            {
                path: '/uikit/menu/',
                component: () => import('@/views/uikit/MenuDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Menu' }]
                }
            },
            {
                path: '/uikit/message',
                name: 'message',
                component: () => import('@/views/uikit/MessagesDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Messages' }]
                }
            },
            {
                path: '/uikit/file',
                name: 'file',
                component: () => import('@/views/uikit/FileDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'File' }]
                }
            },
            {
                path: '/uikit/charts',
                name: 'charts',
                component: () => import('@/views/uikit/ChartDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Charts' }]
                }
            },
            {
                path: '/uikit/timeline',
                name: 'timeline',
                component: () => import('@/views/uikit/TimelineDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Timeline' }]
                }
            },
            {
                path: '/uikit/misc',
                name: 'misc',
                component: () => import('@/views/uikit/MiscDoc.vue'),
                meta: {
                    breadcrumb: [{ parent: 'UI Kit', label: 'Misc' }]
                }
            },
            {
                path: '/pages/crud',
                name: 'crud',
                component: () => import('@/views/pages/Crud.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Pages', label: 'Crud' }]
                }
            },
            {
                path: '/ecommerce/product-overview',
                name: 'product-overview',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'Product Overview' }]
                },
                component: () => import('@/views/e-commerce/ProductOverview.vue')
            },
            {
                path: '/ecommerce/product-list',
                name: 'product-list',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'Product List' }]
                },
                component: () => import('@/views/e-commerce/ProductList.vue')
            },
            {
                path: '/ecommerce/shopping-cart',
                name: 'shopping-cart',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'Shopping Cart' }]
                },
                component: () => import('@/views/e-commerce/ShoppingCart.vue')
            },
            {
                path: '/ecommerce/new-product',
                name: 'new-product',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'New Product' }]
                },
                component: () => import('@/views/e-commerce/NewProduct.vue')
            },
            {
                path: '/ecommerce/order-history',
                name: 'order-history',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'Order History' }]
                },
                component: () => import('@/views/e-commerce/OrderHistory.vue')
            },
            {
                path: '/ecommerce/order-summary',
                name: 'order-summary',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'Order Summary' }]
                },
                component: () => import('@/views/e-commerce/OrderSummary.vue')
            },
            {
                path: '/ecommerce/checkout-form',
                name: 'checkout-form',
                meta: {
                    breadcrumb: [{ parent: 'E-Commerce', label: 'Checkout Form' }]
                },
                component: () => import('@/views/e-commerce/CheckoutForm.vue')
            },
            {
                path: '/profile/list',
                name: 'user-list',
                meta: {
                    breadcrumb: [{ parent: 'User Management', label: 'List' }]
                },
                component: () => import('@/views/user-management/UserList.vue')
            },
            {
                path: '/profile/create',
                meta: {
                    breadcrumb: [{ parent: 'User Management', label: 'Create' }]
                },
                component: () => import('@/views/user-management/create/CreateLayout.vue'),
                children: [
                    {
                        path: '',
                        redirect: '/profile/create/basic-information'
                    },
                    {
                        path: 'basic-information',
                        name: 'user-create-basic',
                        meta: {
                            breadcrumb: [{ parent: 'User Management', label: 'Create', item: 'Basic Information' }]
                        },
                        component: () => import('@/views/user-management/create/BasicInformation.vue')
                    },
                    {
                        path: 'business-information',
                        name: 'user-create-business',
                        meta: {
                            breadcrumb: [{ parent: 'User Management', label: 'Create', item: 'Business Information' }]
                        },
                        component: () => import('@/views/user-management/create/BusinessInformation.vue')
                    },
                    {
                        path: 'location-information',
                        name: 'user-create-location',
                        meta: {
                            breadcrumb: [{ parent: 'User Management', label: 'Create', item: 'Location Information' }]
                        },
                        component: () => import('@/views/user-management/create/LocationInformation.vue')
                    },
                    {
                        path: 'authorization',
                        name: 'user-create-authorization',
                        meta: {
                            breadcrumb: [{ parent: 'User Management', label: 'Create', item: 'Authorization' }]
                        },
                        component: () => import('@/views/user-management/create/Authorization.vue')
                    },
                    {
                        path: 'account-status',
                        name: 'user-create-status',
                        meta: {
                            breadcrumb: [{ parent: 'User Management', label: 'Create', item: 'Account Status' }]
                        },
                        component: () => import('@/views/user-management/create/AccountStatus.vue')
                    }
                ]
            },
            {
                path: '/pages/invoice',
                name: 'invoice',
                component: () => import('@/views/pages/Invoice.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Pages', label: 'Invoice' }]
                }
            },
            {
                path: '/pages/help',
                name: 'help',
                component: () => import('@/views/pages/Help.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Pages', label: 'Help' }]
                }
            },
            {
                path: '/pages/empty',
                name: 'empty',
                meta: {
                    breadcrumb: [{ parent: 'Pages', label: 'Empty' }]
                },
                component: () => import('@/views/pages/Empty.vue')
            },
            {
                path: '/pages/aboutus',
                name: 'aboutus',
                meta: {
                    breadcrumb: [{ parent: 'Pages', label: 'About' }]
                },
                component: () => import('@/views/pages/AboutUs.vue')
            },
            {
                path: '/pages/contact',
                name: 'contact',
                component: () => import('@/views/pages/ContactUs.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Pages', label: 'Contact' }]
                }
            },
            {
                path: '/start/documentation',
                name: 'documentation',
                component: () => import('@/views/utilities/Documentation.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Start', label: 'Documentation' }]
                }
            },
            {
                path: '/blocks/free',
                name: 'blocks',
                component: () => import('@/views/utilities/Blocks.vue'),
                meta: {
                    breadcrumb: [{ parent: 'Prime Blocks', label: 'Free Blocks' }]
                }
            }
        ]
    },
    {
        path: '/auth/login',
        name: 'login',
        component: () => import('@/views/pages/auth/Login.vue')
    },
    {
        path: '/auth/login2',
        name: 'login2',
        component: () => import('@/views/pages/auth/Login2.vue')
    },
    {
        path: '/auth/access',
        name: 'accessDenied',
        component: () => import('@/views/pages/auth/AccessDenied.vue')
    },
    {
        path: '/auth/access2',
        name: 'accessDenied2',
        component: () => import('@/views/pages/auth/AccessDenied2.vue')
    },
    {
        path: '/auth/error',
        name: 'error',
        component: () => import('@/views/pages/auth/Error.vue')
    },
    {
        path: '/auth/error2',
        name: 'error2',
        component: () => import('@/views/pages/auth/Error2.vue')
    },
    {
        path: '/auth/register',
        name: 'register',
        component: () => import('@/views/pages/auth/Register.vue')
    },
    {
        path: '/auth/forgotpassword',
        name: 'forgotpassword',
        component: () => import('@/views/pages/auth/ForgotPassword.vue')
    },
    {
        path: '/auth/newpassword',
        name: 'newpassword',
        component: () => import('@/views/pages/auth/NewPassword.vue')
    },
    {
        path: '/auth/verification',
        name: 'verification',
        component: () => import('@/views/pages/auth/Verification.vue')
    },
    {
        path: '/auth/lockscreen',
        name: 'lockscreen',
        component: () => import('@/views/pages/auth/LockScreen.vue')
    },
    {
        path: '/pages/notfound',
        name: 'notfound',
        component: () => import('@/views/pages/NotFound.vue')
    },
    {
        path: '/landing',
        name: 'landing',
        component: () => import('@/views/pages/Landing.vue')
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'notfound',
        component: () => import('@/views/pages/NotFound.vue')
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { left: 0, top: 0 };
    }
});

export default router;
