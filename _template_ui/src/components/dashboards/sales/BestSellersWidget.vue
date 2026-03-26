<script setup>
import { ref } from 'vue';

const menu = ref(null);
const items = ref([
    { label: 'Update', icon: 'pi pi-fw pi-refresh' },
    { label: 'Edit', icon: 'pi pi-fw pi-pencil' }
]);

const sellers = [
    {
        name: 'Blue Band',
        image: '/demo/images/product/blue-band.jpg'
    },
    {
        name: 'Bracelet',
        image: '/demo/images/product/bracelet.jpg'
    },
    {
        name: 'Black Watch',
        image: '/demo/images/product/black-watch.jpg'
    },
    {
        name: 'Bamboo Watch',
        image: '/demo/images/product/bamboo-watch.jpg'
    },
    {
        name: 'Blue T-Shirt',
        image: '/demo/images/product/blue-t-shirt.jpg'
    },
    {
        name: 'Game Controller',
        image: '/demo/images/product/game-controller.jpg'
    },
    {
        name: 'Phone Case',
        image: '/demo/images/product/gold-phone-case.jpg'
    }
];

function toggleMenu(event) {
    menu.value.toggle(event);
}
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="font-semibold text-xl m-0">Best Sellers</span>
            <div>
                <Button icon="pi pi-ellipsis-h" rounded text plain @click="toggleMenu" />
                <Menu ref="menu" popup :model="items" />
            </div>
        </div>

        <ul class="m-0 p-0 border-0 outline-0 list-none">
            <li class="py-4 px-0">
                <div v-for="(seller, index) in sellers" :key="index" class="h-16 border border-surface rounded-xl flex items-center p-4 mb-2 cursor-pointer hover:bg-emphasis transition-colors duration-150">
                    <img width="32px" height="32px" class="rounded-full mr-4" :src="seller.image" :alt="seller.name" />
                    <span>{{ seller.name }}</span>
                    <span class="ml-auto">
                        <a href="#"><i class="pi pi-chevron-right text-muted-color"></i></a>
                    </span>
                </div>
            </li>
        </ul>
    </div>
</template>

<style scoped>
.table-responsive {
    overflow-x: auto;
}
</style>
