<script setup>
import AppConfig from '@/layout/AppConfig.vue';
import { ref } from 'vue';

const value1 = ref(null);
const value2 = ref(null);
const value3 = ref(null);
const value4 = ref(null);

function focus(event) {
    const regexNum = /^\d+$/;
    const isValid = regexNum.test(event.key);
    const nextElementInputRef = event.currentTarget.nextElementSibling.children[0];

    isValid && nextElementInputRef.focus();
}
</script>

<template>
    <div class="h-screen flex w-full bg-surface-50 dark:bg-surface-950">
        <div class="flex flex-1 flex-col bg-surface-50 dark:bg-surface-950 items-center justify-center">
            <div class="w-11/12 sm:w-[30rem]">
                <div class="flex flex-col">
                    <div style="height: 56px; width: 56px" class="bg-primary rounded-full flex items-center justify-center">
                        <i class="pi pi-check-circle text-surface-0 dark:text-surface-900 text-4xl!"></i>
                    </div>
                    <div class="mt-6">
                        <h1 class="m-0 text-primary font-semibold text-4xl">Authentication?</h1>
                        <span class="block text-surface-700 dark:text-surface-100 mt-2">Verify your code</span>
                    </div>
                </div>
                <Fluid class="flex gap-4 items-center mt-12">
                    <InputNumber inputId="val1" v-model="value1" inputClass="text-center" :max="9" @keyup="focus($event)"></InputNumber>
                    <InputNumber inputId="val2" v-model="value2" inputClass="text-center" :max="9" @keyup="focus($event)"></InputNumber>
                    <InputNumber inputId="val3" v-model="value3" inputClass="text-center" :max="9" @keyup="focus($event)"></InputNumber>
                    <InputNumber inputId="val4" v-model="value4" inputClass="text-center" :max="9"></InputNumber>
                </Fluid>
                <div class="mt-4">
                    <Button class="w-full" label="VERIFY NOW"></Button>
                </div>
                <div class="mt-4">
                    <Button class="w-full text-primary-500" text label="SEND AGAIN"></Button>
                </div>
            </div>
        </div>
        <div :style="{ backgroundImage: 'url(/demo/images/pages/accessDenied-bg.jpg)' }" class="hidden lg:flex flex-1 items-center justify-center bg-cover">
            <img src="/layout/images/logo/vector_logo.png" alt="" />
        </div>
    </div>

    <AppConfig simple />
</template>
