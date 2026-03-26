import { computed, reactive } from 'vue'

const layoutConfig = reactive({
  menuMode: 'static',
})

const layoutState = reactive({
  staticMenuInactive: false,
  overlayMenuActive: false,
  mobileMenuActive: false,
  activePath: null,
})

export function useLayout() {
  const isDesktop = () => window.innerWidth > 991

  const toggleMenu = () => {
    if (isDesktop()) {
      if (layoutConfig.menuMode === 'static') {
        layoutState.staticMenuInactive = !layoutState.staticMenuInactive
      } else {
        layoutState.overlayMenuActive = !layoutState.overlayMenuActive
      }
    } else {
      layoutState.mobileMenuActive = !layoutState.mobileMenuActive
    }
  }

  const hideMobileMenu = () => {
    layoutState.mobileMenuActive = false
    layoutState.overlayMenuActive = false
  }

  const containerClass = computed(() => ({
    'layout-static': layoutConfig.menuMode === 'static',
    'layout-overlay': layoutConfig.menuMode === 'overlay',
    'layout-static-inactive': layoutState.staticMenuInactive,
    'layout-overlay-active': layoutState.overlayMenuActive,
    'layout-mobile-active': layoutState.mobileMenuActive,
    'layout-menu-light': true,
    'layout-topbar-lightblue': true,
  }))

  return {
    layoutConfig,
    layoutState,
    containerClass,
    toggleMenu,
    hideMobileMenu,
    isDesktop,
  }
}

