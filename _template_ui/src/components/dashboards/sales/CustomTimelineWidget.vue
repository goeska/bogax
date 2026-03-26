<script setup>
import { ref } from 'vue';

const menu = ref(null);

const timelineEvents = ref([
    { status: 'Ordered', date: '15/10/2024 10:30', icon: 'pi pi-shopping-cart', color: '#E91E63', description: 'Richard Jones (C8012) has ordered a blue t-shirt for $79.' },
    { status: 'Processing', date: '15/10/2024 14:00', icon: 'pi pi-cog', color: '#FB8C00', description: 'Order #99207 has processed succesfully.' },
    { status: 'Shipped', date: '15/10/2024 16:15', icon: 'pi pi-compass', color: '#673AB7', description: 'Order #99207 has shipped with shipping code 2222302090.' },
    { status: 'Delivered', date: '16/10/2024 10:00', icon: 'pi pi-check-square', color: '#0097A7', description: 'Richard Jones (C8012) has recieved his blue t-shirt.' }
]);

const items = ref([
    { label: 'Update', icon: 'pi pi-fw pi-refresh' },
    { label: 'Edit', icon: 'pi pi-fw pi-pencil' }
]);

function toggleMenu(event) {
    menu.value.toggle(event);
}
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="font-semibold text-xl m-0">Timeline</span>
            <div>
                <Button icon=" pi pi-ellipsis-h" rounded text plain @click="toggleMenu"></Button>
                <Menu ref="menu" popup :model="items"> </Menu>
            </div>
        </div>

        <Timeline :value="timelineEvents" align="left" class="customized-timeline">
            <template #marker="slotProps">
                <span class="shadow w-8 h-8 rounded-full flex justify-center items-center" :style="{ backgroundColor: slotProps.item.color }">
                    <i class="text-white" :class="slotProps.item.icon"></i>
                </span>
            </template>
            <template #content="slotProps">
                <Card class="mb-4 shadow-none! border border-surface rounded-xl!">
                    <template #title>
                        {{ slotProps.item.status }}
                    </template>
                    <template #subtitle>
                        {{ slotProps.item.date }}
                    </template>
                    <template #content>
                        <img v-if="slotProps.item.image" :src="'assets/showcase/images/demo/product/' + slotProps.item.image" :alt="slotProps.item.name" width="200" class="shadow" />
                        <p>{{ slotProps.item.description }}</p>
                    </template>
                </Card>
            </template>
        </Timeline>
    </div>
</template>

<style lang="scss" scoped>
::v-deep(.customized-timeline) {
    .p-timeline-event:nth-child(even) {
        flex-direction: row !important;

        .p-timeline-event-content {
            text-align: left !important;
        }
    }

    .p-timeline-event-opposite {
        flex: 0;
    }
}
</style>
