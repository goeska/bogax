<script setup>
import CollaborationWidget from '@/components/landing/CollaborationWidget.vue';
import EasyFollowWidget from '@/components/landing/EasyFollowWidget.vue';
import FeaturesWidget from '@/components/landing/FeaturesWidget.vue';
import FooterWidget from '@/components/landing/FooterWidget.vue';
import HeroWidget from '@/components/landing/HeroWidget.vue';
import NewsletterWidget from '@/components/landing/NewsletterWidget.vue';
import ShowReelsWidget from '@/components/landing/ShowReelsWidget.vue';
import Topbar from '@/components/landing/TopbarWidget.vue';
import WhoUsesWidget from '@/components/landing/WhoUsesWidget.vue';
import { useLayout } from '@/layout/composables/layout';
import { onBeforeMount } from 'vue';

const { layoutConfig, isDarkTheme } = useLayout();

function executeDarkModeToggle() {
    layoutConfig.darkTheme = !layoutConfig.darkTheme;
    layoutConfig.menuTheme = isDarkTheme.value ? 'dark' : 'light';

    document.documentElement.classList.toggle('app-dark');
}

onBeforeMount(() => {
    if (!layoutConfig.darkTheme) {
        if (!document.startViewTransition) {
            executeDarkModeToggle();

            return;
        }

        document.startViewTransition(() => executeDarkModeToggle(event));
    }
});
</script>

<template>
    <div class="bg-surface-50 dark:bg-surface-950">
        <Topbar />

        <div class="h-screen">
            <div style="perspective: 101px" class="h-screen overflow-x-hidden overflow-y-auto absolute top-0 left-0 right-0 bottom-0">
                <HeroWidget />
                <div id="parallaxBody" class="lg:top-full block absolute left-0 right-0 h-full z-20">
                    <WhoUsesWidget />
                    <FeaturesWidget>
                        <CollaborationWidget />
                        <EasyFollowWidget />
                        <ShowReelsWidget />
                        <NewsletterWidget />
                        <FooterWidget />
                    </FeaturesWidget>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
::placeholder {
    color: #fff;
}
</style>
