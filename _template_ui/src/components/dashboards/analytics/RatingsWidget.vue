<script setup>
import { useLayout } from '@/layout/composables/layout';
import { onMounted, ref, watch } from 'vue';

const {layoutConfig,isDarkTheme } = useLayout();

const optionValue = ref({ label: 'Weekly', value: 'weekly' });
const expensesData = ref(null);
const expensesOptions = ref(null);

const stateOptions = ref([
    { label: 'Weekly', value: 'weekly' },
    { label: 'Monthly', value: 'monthly' }
]);

const ratings = ref([
    {
        title: 'Product Questions',
        value: '23',
        icon: 'pi pi-arrow-up-right',
        items: [
            {
                image: '/demo/images/product/black-watch.jpg',
                title: 'Black Watch',
                description: 'Is the Black Watch product water-resistant?'
            },
            {
                image: '/demo/images/product/blue-t-shirt.jpg',
                title: 'Blue T-Shirt',
                description: 'Can I return or exchange the blue t-shirt if I am not satisfied with it?'
            }
        ]
    },
    {
        title: 'Product Reviews',
        value: '54',
        icon: 'pi pi-arrow-up-right',
        items: [
            {
                image: '/demo/images/product/blue-band.jpg',
                title: 'Blue Band',
                description: 'Loved the blue band from this e-commerce site!'
            },
            {
                image: '/demo/images/product/bamboo-watch.jpg',
                title: 'Bamboo Watch',
                description: "I purchased the bamboo watch and I'm really happy with it."
            }
        ]
    },
    {
        title: 'Shipping Orders',
        value: '99+',
        icon: 'pi pi-arrow-up-right',
        items: [
            {
                image: '/demo/images/product/black-watch.jpg',
                title: 'Black Watch',
                description: 'Last Shipping Date'
            },
            {
                image: '/demo/images/product/bamboo-watch.jpg',
                title: 'Blue T-Shirt',
                description: 'Last Shipping Date'
            }
        ]
    }
]);

function setExpensesData() {
    return {
        labels: ['January', 'February', 'March', 'April', 'May', 'June'],
        datasets: [
            {
                data: [30, 10, 32, 15, 20, 40],
                borderColor: [getComputedStyle(document.body).getPropertyValue('--p-primary-color')],
                backgroundColor: [isDarkTheme.value ? `color-mix(in srgb, ${getComputedStyle(document.body).getPropertyValue('--p-primary-200')}, transparent 84%)` : getComputedStyle(document.body).getPropertyValue('--p-primary-50')],
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }
        ]
    };
}

function setExpensesOptions() {
    return {
        plugins: {
            legend: {
                display: false
            }
        },
        maintainAspectRatio: false,
        responsive: true,
        aspectRatio: 4,
        scales: {
            y: {
                display: false,
                beginAtZero: true
            },
            x: {
                display: false
            }
        },
        tooltips: {
            enabled: false
        },
        elements: {
            point: {
                radius: 5,
                pointBackgroundColor: [getComputedStyle(document.body).getPropertyValue('--p-primary-800')]
            }
        }
    };
}

onMounted(() => {
    expensesData.value = setExpensesData();
    expensesOptions.value = setExpensesOptions();
});

watch([() => layoutConfig.primary, isDarkTheme], () => {
    expensesData.value = setExpensesData();
    expensesOptions.value = setExpensesOptions();
});
</script>

<template>
    <div class="card h-full">
        <div class="flex flex-col gap-4">
            <div class="flex flex-col p-4 gap-4 w-full justify-between rounded-md">
                <div class="flex justify-between items-center">
                    <span class="text-xl font-semibold m-0">Ratings</span>
                    <SelectButton v-model="optionValue" :options="stateOptions" optionLabel="label"></SelectButton>
                </div>
                <div>
                    <Chart type="line" :data="expensesData" :options="expensesOptions"></Chart>
                </div>
            </div>
            <div class="flex flex-col lg:flex-row gap-4 justify-between flex-1">
                <template v-for="(rating, index) in ratings" :key="index">
                    <div class="flex flex-col p-4 w-full border border-surface rounded-xl gap-4">
                        <div class="flex justify-between">
                            <div class="flex flex-col gap-1">
                                <span class="text-surface-900 dark:text-surface-0 text-4xl">{{ rating.value }}</span>
                                <span class="text-surface-700 dark:text-surface-100">{{ rating.title }}</span>
                            </div>
                            <a href="#/dashboard-analytics">
                                <i :class="[rating.icon, 'text-surface-900 dark:text-surface-0 text-2xl']"></i>
                            </a>
                        </div>
                        <div class="flex flex-col gap-2">
                            <template v-for="(item, itemIndex) in rating.items" :key="itemIndex">
                                <div class="flex gap-2 p-2 bg-surface-0 dark:bg-surface-900 shadow-sm rounded-md">
                                    <img :src="item.image" class="w-8 h-8 rounded-full" />
                                    <div class="flex flex-col gap-1">
                                        <span class="text-sm font-medium text-surface-900 dark:text-surface-0">{{ item.title }}</span>
                                        <span class="text-sm text-surface-900 dark:text-surface-0">{{ item.description }}</span>
                                    </div>
                                </div>
                            </template>
                        </div>
                    </div>
                </template>
            </div>
        </div>
    </div>
</template>
