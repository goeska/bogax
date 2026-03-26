<script setup>
import { ref } from 'vue';

const menu = ref();
const searches = ref([
    {
        name: 'Mat Orange Case',
        rate: '82'
    },
    {
        name: 'Space T-Shirt',
        rate: '78'
    },
    {
        name: 'Orange Black Hoodie',
        rate: '61'
    },
    {
        name: 'Wonders Notebook',
        rate: '48'
    },
    {
        name: 'Robots T-Shirt',
        rate: '34'
    },
    {
        name: 'Green Portal Sticker',
        rate: '11'
    }
]);

const items = ref([
    { label: 'View', icon: 'pi pi-eye' },
    { label: 'Export', icon: 'pi pi-upload' }
]);

function toggleMenu(event) {
    menu.value.toggle(event);
}
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="text-xl font-semibold m-0">Top Searches</span>
            <div>
                <Button icon="pi pi-ellipsis-h" rounded text plain @click="toggleMenu" />
                <Menu ref="menu" popup :model="items" />
            </div>
        </div>
        <template v-for="(search, index) in searches" :key="index">
            <div :class="['flex justify-between', index % 2 === 0 ? 'bg-surface-50 dark:bg-surface-800' : '', 'p-4']">
                <span>{{ search.name }}</span>
                <span :class="['font-medium', search.rate >= 60 ? 'text-green-500' : search.rate >= 40 ? 'text-orange-500' : 'text-pink-500']">{{ search.rate }}% CONV RATE</span>
            </div>
        </template>
    </div>
</template>
