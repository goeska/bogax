<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const { layoutState, layoutConfig, isHorizontal, isSlim, isProfileMenuActive, isDesktop } = useLayout();
const outsideClickListener = ref(null);

const menuClass = computed(() => (isHorizontal.value ? 'overlay' : null));

function toggleMenu() {
    const menu = document.querySelector('.menu-transition');

    if (isProfileMenuActive.value) {
        menu.style.maxHeight = '0';
        menu.style.opacity = '0';
        if (isHorizontal.value) {
            menu.style.transform = 'scaleY(0.8)';
        }
    } else {
        menu.style.maxHeight = menu.scrollHeight + 'px';
        menu.style.opacity = '1';
        if (isHorizontal.value) {
            menu.style.transform = 'scaleY(1)';

            if (isDesktop()) {
                layoutState.activePath = null;
                layoutState.menuHoverActive = false;
            }
        }
    }

    layoutState.menuProfileActive = !layoutState.menuProfileActive;
}

const iconClass = computed(() => {
    const profilePositionStart = layoutConfig.menuProfilePosition === 'start';

    return {
        'pi-angle-up': (isProfileMenuActive.value && (profilePositionStart || isHorizontal.value)) || (!isProfileMenuActive.value && !profilePositionStart && !isHorizontal.value),
        'pi-angle-down': (!isProfileMenuActive.value && profilePositionStart) || (isProfileMenuActive.value && !profilePositionStart) || isHorizontal.value
    };
});

function tooltipValue(tooltipText) {
    return isSlim.value ? tooltipText : null;
}

function unbindOutsideClickListener() {
    if (outsideClickListener.value) {
        document.removeEventListener('click', outsideClickListener.value);
        outsideClickListener.value = null;
    }
}

function bindOutsideClickListener() {
    if (!outsideClickListener.value) {
        outsideClickListener.value = (event) => {
            if (isOutsideClicked(event)) {
                toggleMenu();
            }
        };
        document.addEventListener('click', outsideClickListener.value);
    }
}

function isOutsideClicked(event) {
    const sidebarEl = document.querySelector('.layout-menu-profile');
    const topbarButtonEl = document.querySelector('.layout-menu-profile-button');

    return !(sidebarEl?.isSameNode(event.target) || sidebarEl?.contains(event.target) || topbarButtonEl?.isSameNode(event.target) || topbarButtonEl?.contains(event.target));
}

watch(isProfileMenuActive, (newVal) => {
    if (layoutConfig.menuMode === 'horizontal') {
        if (newVal) {
            bindOutsideClickListener();
        } else {
            unbindOutsideClickListener();
        }
    }
});

onBeforeUnmount(() => {
    unbindOutsideClickListener();
});
</script>

<template>
    <div class="layout-menu-profile">
        <button class="layout-menu-profile-button" v-tooltip="{ value: tooltipValue('Profile') }" @click="toggleMenu">
            <img src="/layout/images/avatar/amyelsner.png" alt="avatar" style="width: 32px; height: 32px" />
            <span class="text-start">
                <strong>Amy Elsner</strong>
                <small>Webmaster</small>
            </span>
            <i class="layout-menu-profile-toggler pi pi-fw" :class="iconClass"></i>
        </button>

        <ul :class="['menu-transition', menuClass]" style="overflow: hidden; max-height: 0; opacity: 0">
            <li v-tooltip="{ value: tooltipValue('Settings') }">
                <button @click="router.push('/start/documentation')">
                    <i class="pi pi-cog pi-fw"></i>
                    <span>Settings</span>
                </button>
            </li>

            <li v-tooltip="{ value: tooltipValue('Profile') }">
                <button @click="router.push('/start/documentation')">
                    <i class="pi pi-file-o pi-fw"></i>
                    <span>Profile</span>
                </button>
            </li>
            <li v-tooltip="{ value: tooltipValue('Support') }">
                <button @click="router.push('/start/documentation')">
                    <i class="pi pi-compass pi-fw"></i>
                    <span>Support</span>
                </button>
            </li>
            <li v-tooltip="{ value: tooltipValue('Logout') }">
                <button @click="router.push('/auth/login2')">
                    <i class="pi pi-power-off pi-fw"></i>
                    <span>Logout</span>
                </button>
            </li>
        </ul>
    </div>
</template>

<style scoped>
.menu-transition {
    transition:
        max-height 400ms cubic-bezier(0.86, 0, 0.07, 1),
        opacity 400ms cubic-bezier(0.86, 0, 0.07, 1);
}
.menu-transition.overlay {
    transition:
        opacity 100ms linear,
        transform 120ms cubic-bezier(0, 0, 0.2, 1);
}
</style>
