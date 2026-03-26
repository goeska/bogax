<script setup>
import { ref } from 'vue';

const menu = ref(null);
const contacts = ref([
    {
        name: 'Xuxue Feng',
        email: 'feng@ultima.org',
        avatar: '/demo/images/avatar/xuxuefeng.png',
        tags: ['Accounting', 'Sales']
    },
    {
        name: 'Elwin Sharvill',
        email: 'sharvill@ultima.org',
        avatar: '/demo/images/avatar/elwinsharvill.png',
        tags: ['Finance', 'Sales']
    },
    {
        name: 'Anna Fali',
        email: 'fali@ultima.org',
        avatar: '/demo/images/avatar/asiyajavayant.png',
        tags: ['Management']
    },
    {
        name: 'Jon Stone',
        email: 'stone@ultima.org',
        avatar: '/demo/images/avatar/ivanmagalhaes.png',
        tags: ['Management', 'Finance']
    },
    {
        name: 'Stephen Shaw',
        email: 'shaw@ultima.org',
        avatar: '/demo/images/avatar/stephenshaw.png',
        tags: ['Finance']
    }
]);

const items = ref([
    { label: 'New', icon: 'pi pi-fw pi-plus' },
    { label: 'Edit', icon: 'pi pi-fw pi-pencil' },
    { label: 'Delete', icon: 'pi pi-fw pi-trash' }
]);

function toggleMenu(event) {
    menu.value.toggle(event);
}
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="font-semibold text-xl m-0">Contact</span>
            <div>
                <Button icon="pi pi-ellipsis-h" rounded text plain @click="toggleMenu"></Button>
                <Menu ref="menu" popup :model="items"> </Menu>
            </div>
        </div>
        <ul class="p-0 m-0 border-0 list-none">
            <li v-for="contact in contacts" :key="contact.email" class="flex items-center py-4 justify-between">
                <div class="flex items-center">
                    <img :src="contact.avatar" />
                    <div class="ml-2">
                        <div>{{ contact.name }}</div>
                        <small class="text-muted-color">{{ contact.email }}</small>
                    </div>
                </div>
                <div class="flex gap-2">
                    <Tag v-for="tag in contact.tags" :key="tag" severity="secondary">{{ tag }}</Tag>
                </div>
            </li>
        </ul>
    </div>
</template>
