<script setup>
import AppConfig from '@/layout/AppConfig.vue';
import { useRouter } from 'vue-router';

const router = useRouter();

function navigateToDashboard() {
    router.push('/');
}
</script>

<template>
    <div class="h-screen flex w-full">
        <div class="flex flex-1 flex-col bg-surface-50 dark:bg-surface-950 justify-center">
            <div class="flex justify-center">
                <img src="/demo/images/pages/accessDenied.png" alt="" />
            </div>
            <div class="flex flex-col gap-2 items-center">
                <span class="text-4xl m-0 text-orange-600 font-semibold">ACCESS DENIED!</span>
                <span class="text-surface-700 dark:text-surface-100">You do not have the permissions.</span>
            </div>
            <div class="flex justify-center mt-12">
                <Button type="button" label="BACK TO DASHBOARD" @click="navigateToDashboard" class="bg-indigo-500! text-white!" text></Button>
            </div>
        </div>
        <div :style="{ backgroundImage: 'url(/demo/images/pages/accessDenied-bg.jpg)' }" class="hidden lg:flex flex-1 items-center justify-center bg-cover">
            <img src="/layout/images/logo/vector_logo.png" alt="" />
        </div>
    </div>
    <AppConfig simple />
</template>
