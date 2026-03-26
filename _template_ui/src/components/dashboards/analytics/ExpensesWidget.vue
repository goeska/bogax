<script setup>
import { onMounted, ref } from 'vue';

const menu = ref();
const expenses = ref([
    {
        icon: 'pi pi-cloud',
        amount: '30.247',
        category: 'Cloud Infrastructure'
    },
    {
        icon: 'pi pi-tag',
        amount: '29.550',
        category: 'General Goods'
    },
    {
        icon: 'pi pi-desktop',
        amount: '16.660',
        category: 'Consumer Electronics'
    },
    {
        icon: 'pi pi-compass',
        amount: '5.801',
        category: 'Incalculables'
    }
]);

const updateInterval = ref(null);

const items = ref([
    { label: 'View', icon: 'pi pi-eye' },
    { label: 'Export', icon: 'pi pi-upload' }
]);

function toggleMenu(event) {
    menu.value.toggle(event);
}

onMounted(() => {
    if (updateInterval.value) {
        clearInterval(updateInterval.value);
    }
});
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="text-xl font-semibold m-0">Expenses</span>
            <div>
                <Button icon="pi pi-ellipsis-h" rounded text plain @click="toggleMenu" />
                <Menu ref="menu" popup :model="items" />
            </div>
        </div>
        <div class="border-b border-surface text-sm text-muted-color mb-2 pb-4">November 22 - November 29</div>

        <template v-for="(expense, index) in expenses" :key="index">
            <div :class="['flex justify-between items-center my-2 p-2', index !== expenses.length - 1 ? 'border-b border-surface' : '']">
                <div class="flex flex-col">
                    <i :class="[expense.icon, 'text-cyan-700 text-2xl mb-2']" />
                    <span class="font-medium mb-1">${{ expense.amount }}</span>
                    <span class="text-muted-color">{{ expense.category }}</span>
                </div>
                <span>
                    <a href="#" class="text-muted-color">
                        <i class="pi pi-chevron-right" />
                    </a>
                </span>
            </div>
        </template>
    </div>
</template>
