<script setup>
import AppConfig from '@/layout/AppConfig.vue';
</script>

<template>
    <div class="h-screen flex w-full bg-surface-50 dark:bg-surface-950">
        <div class="flex flex-1 flex-col bg-surface-50 dark:bg-surface-950 items-center justify-center">
            <div class="w-11/12 sm:w-[30rem]">
                <div class="flex flex-col">
                    <div style="height: 56px; width: 56px" class="bg-primary rounded-full flex items-center justify-center">
                        <i class="pi pi-key text-surface-0 dark:text-surface-900 text-4xl!"></i>
                    </div>
                    <div class="mt-6">
                        <h1 class="m-0 text-primary font-semibold text-4xl">Choose your new password!</h1>
                        <span class="block text-surface-700 dark:text-surface-100 mt-2">Enter your new password</span>
                    </div>
                </div>
                <div class="flex flex-col gap-4 mt-12">
                    <InputGroup>
                        <InputGroupAddon>
                            <i class="pi pi-key"></i>
                        </InputGroupAddon>
                        <Password id="password" placeholder="Password" inputClass="w-full" toggleMask></Password>
                    </InputGroup>
                    <InputGroup>
                        <InputGroupAddon>
                            <i class="pi pi-key z-20"></i>
                        </InputGroupAddon>
                        <Password id="password" placeholder="Repeat Password" inputClass="w-full" toggleMask></Password>
                    </InputGroup>
                    <InputGroup>
                        <Button class="w-full" label="SAVE NEW PASSWORD"></Button>
                    </InputGroup>
                    <InputGroup>
                        <Button class="w-full text-primary-500" text label="BACK TO LOGIN"></Button>
                    </InputGroup>
                </div>
            </div>
        </div>
        <div :style="{ backgroundImage: 'url(/demo/images/pages/accessDenied-bg.jpg)' }" class="hidden lg:flex flex-1 items-center justify-center bg-cover">
            <img src="/layout/images/logo/vector_logo.png" alt="" />
        </div>
    </div>
    <AppConfig simple />
</template>
