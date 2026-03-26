<script setup>
import AppConfig from '@/layout/AppConfig.vue';
import { useRouter } from 'vue-router';

const router = useRouter();

function navigateToDashboard() {
    router.push('/');
}
</script>

<template>
    <div class="min-h-screen flex flex-col bg-cover" :style="{ backgroundImage: 'url(/demo/images/pages/accessDenied-bg.jpg)' }">
        <div class="self-center mt-auto mb-auto">
            <div class="text-center z-40 rounded-lg border border-surface bg-white p-4 shadow-md flex flex-col">
                <div class="rounded-md mx-auto border border-surface bg-orange-500 -mt-12 px-4 py-1">
                    <span class="m-0 text-3xl font-semibold text-surface-0 dark:text-surface-900">ACCESS DENIED</span>
                </div>
                <div class="bg-surface-200 dark:bg-surface-600 p-4 mb-8 shadow rounded-md mt-4 px-12">
                    <img src="/demo/images/pages/accessDenied.png" alt="" />
                </div>
                <div class="text-muted-color pb-12">You do not have the permissions.</div>
                <Button type="button" label="GO BACK TO DASHBOARD" @click="navigateToDashboard" text></Button>
            </div>
        </div>
    </div>
    <AppConfig simple />
</template>
