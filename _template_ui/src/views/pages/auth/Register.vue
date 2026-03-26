<script setup>
import AppConfig from '@/layout/AppConfig.vue';
import { ref } from 'vue';

const value1 = ref(null);
const value2 = ref(null);
</script>

<template>
    <div class="h-screen flex w-full bg-surface-50 dark:bg-surface-950">
        <div class="flex flex-1 flex-col bg-surface-50 dark:bg-surface-950 items-center justify-center">
            <div class="w-11/12 sm:w-[30rem]">
                <div class="flex flex-col">
                    <div style="height: 56px; width: 56px" class="bg-primary rounded-full flex items-center justify-center">
                        <i class="pi pi-users text-surface-0 dark:text-surface-900 text-4xl!"></i>
                    </div>
                    <div class="mt-6">
                        <h1 class="m-0 text-primary font-semibold text-4xl">Join us!</h1>
                        <span class="block text-surface-700 dark:text-surface-100 mt-2">Please fill the fields to sign-up Ultima network</span>
                    </div>
                </div>
                <div class="flex flex-col gap-4 mt-12">
                    <InputGroup>
                        <InputGroupAddon>
                            <i class="pi pi-user"></i>
                        </InputGroupAddon>
                        <InputText placeholder="Name" />
                    </InputGroup>
                    <InputGroup>
                        <InputGroupAddon>
                            <i class="pi pi-at"></i>
                        </InputGroupAddon>
                        <InputText placeholder="Email" />
                    </InputGroup>
                    <InputGroup>
                        <InputGroupAddon>
                            <i class="pi pi-key"></i>
                        </InputGroupAddon>
                        <Password id="password" v-model="value1" placeholder="Password" inputClass="w-full" toggleMask />
                    </InputGroup>
                    <InputGroup>
                        <InputGroupAddon>
                            <i class="pi pi-key"></i>
                        </InputGroupAddon>
                        <Password id="password" v-model="value2" placeholder="Password Again" inputClass="w-full" toggleMask />
                    </InputGroup>
                    <div>
                        <Button class="w-full" label="SIGN UP"></Button>
                    </div>
                    <div>
                        <Button class="w-full text-primary-500" text label="BACK TO LOGIN"></Button>
                    </div>
                </div>
            </div>
        </div>
        <div :style="{ backgroundImage: 'url(/demo/images/pages/accessDenied-bg.jpg)' }" class="hidden lg:flex flex-1 items-center justify-center bg-cover">
            <img src="/layout/images/logo/vector_logo.png" alt="" />
        </div>
    </div>
    <AppConfig simple />
</template>
