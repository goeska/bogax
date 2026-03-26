<script setup>
import { ref } from 'vue';

const todos = ref([
    {
        name: 'tasks',
        quantity: 72
    },
    {
        name: 'production',
        quantity: 4
    },
    {
        name: 'tests',
        quantity: 18
    },
    {
        name: 'meetings',
        quantity: 13
    }
]);
</script>

<template>
    <div class="card h-full">
        <div class="p-2 h-full flex flex-col justify-between">
            <div class="flex aling-items-center justify-between mb-4">
                <div class="flex gap-4 flex-col justify-between w-full md:flex-row md:items-center">
                    <div class="flex gap-4 items-center">
                        <div class="text-4xl">👋</div>
                        <div class="flex flex-col gap-1 text-surface-600 dark:text-surface-200">
                            <span class="text-2xl font-semibold">Hi,<span class="text-color"> Amy!</span></span>
                            <span>Team Lead <span class="font-bold text-primary">@UX Designer</span></span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2">
                        <Button label="Enroll a Ticket" icon="pi pi-send" outlined></Button>
                        <Button label="Upgrade Your Plan" icon="pi pi-chart-line"></Button>
                    </div>
                </div>
            </div>
            <div class="flex flex-col gap-2 text-primary mt-6 md:mt-0">
                <span class="font-bold text-sm">Done in Current Month</span>
                <div class="grid grid-cols-12 gap-4 grid-nogutter font-medium">
                    <span v-for="todo in todos" :key="todo.name" class="col-span-6 text-6xl md:col-span-3 flex items-center">
                        {{ todo.quantity }}
                        <span class="text-base ml-2">{{ todo.name }}</span>
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>
