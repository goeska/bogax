<script setup>
import AppConfig from '@/layout/AppConfig.vue';
</script>

<template>
    <div class="min-h-screen flex flex-col bg-cover" :style="{ backgroundImage: 'url(/demo/images/pages/login-bg.jpg)' }">
        <div class="self-center mt-auto mb-auto">
            <div class="text-center z-50 flex flex-col border rounded-md border-surface bg-surface-0 dark:bg-surface-900 p-12">
                <span class="text-2xl font-semibold">Welcome</span>
                <div class="text-muted-color mb-12 px-12">Please use the form to sign-in Ultima network</div>

                <div class="w-full flex flex-col gap-4 px-4">
                    <IconField>
                        <InputIcon class="pi pi-envelope" />
                        <InputText class="w-full" placeholder="E-mail" />
                    </IconField>

                    <IconField>
                        <InputIcon class="pi pi-key" />
                        <InputText type="password" class="w-full" placeholder="Password" />
                    </IconField>
                    <Button @click="$router.push('/')" class="w-full mt-4 px-4" label="LOGIN"></Button>
                </div>
            </div>
        </div>
    </div>
    <AppConfig simple />
</template>
