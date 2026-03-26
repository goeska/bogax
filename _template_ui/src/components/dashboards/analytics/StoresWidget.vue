<script setup>
import { useLayout } from '@/layout/composables/layout';
import Chart from 'primevue/chart';
import { computed, onMounted, ref, watch } from 'vue';

const { layoutConfig,isDarkTheme } = useLayout();
const storeInterval = ref(null);

const stores = ref([
    {
        id: 'A',
        name: 'Store A',
        totalValue: 157.5,
        diff: 0,
        status: 0,
        growth: '8.5'
    },
    {
        id: 'B',
        name: 'Store B',
        totalValue: 124.25,
        diff: 0,
        status: 0,
        growth: '-3.2'
    },
    {
        id: 'C',
        name: 'Store C',
        totalValue: 189.99,
        diff: 0,
        status: 0,
        growth: '12.4'
    },
    {
        id: 'D',
        name: 'Store D',
        totalValue: 142.75,
        diff: 0,
        status: 0,
        growth: '-6.8'
    }
]);

const storeData = {
    A: ref(null),
    B: ref(null),
    C: ref(null),
    D: ref(null)
};

const initialData = {
    A: [55, 3, 45, 6, 44, 58, 84, 68, 64],
    B: [81, 75, 63, 100, 69, 79, 38, 37, 76],
    C: [99, 55, 22, 72, 24, 79, 35, 91, 48],
    D: [5, 51, 68, 82, 28, 21, 29, 45, 44]
};

const getStoreData = (initialData) => ({
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'],
    datasets: [
        {
            data: initialData,
            borderColor: [getComputedStyle(document.body).getPropertyValue('--p-primary-color')],
            backgroundColor: [isDarkTheme.value ? `color-mix(in srgb, ${getComputedStyle(document.body).getPropertyValue('--p-primary-200')}, transparent 84%)` : getComputedStyle(document.body).getPropertyValue('--p-primary-50')],
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }
    ]
});

const chartOptions = computed(() => ({
    plugins: {
        legend: {
            display: false
        }
    },
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
            radius: 0
        }
    },
    animation: {
        animateScale: true,
        animateRotate: true
    }
}));

const calculateStore = (storeId, store) => {
    let randomNumber = +(Math.random() * 500).toFixed(2);
    let data = [...storeData[storeId].value.datasets[0].data];
    let length = data.length;
    data.push(randomNumber);
    data.shift();
    storeData[storeId].value.datasets[0].data = data;

    let diff = +(data[length - 1] - data[length - 2]).toFixed(2);
    let status = diff === 0 ? 0 : diff > 0 ? 1 : -1;
    store.totalValue = +(store.totalValue + diff).toFixed(2);
    store.diff = diff;
    store.status = status;
};

const refreshCharts = () => {
    Object.keys(initialData).forEach((storeId) => {
        storeData[storeId].value = getStoreData(initialData[storeId]);
    });
};

onMounted(() => {
    refreshCharts();
    storeInterval.value = setInterval(() => {
        requestAnimationFrame(() => {
            stores.value.forEach((store) => {
                calculateStore(store.id, store);
            });
        });
    }, 2000);
});

watch([() => layoutConfig.primary, isDarkTheme], () => {
    refreshCharts();
});
</script>

<template>
    <div class="card grid grid-cols-12 gap-4 grid-nogutter">
        <div v-for="store in stores" :key="store.id" class="lg:col-span-3 md:col-span-6 sm:col-span-12 p-0">
            <div class="flex flex-col p-6">
                <div class="text-muted-color mb-2">Store {{ store.id }} Sales</div>
                <div class="flex items-center mb-3">
                    <div class="border-round inline-flex items-baseline justify-center">
                        <i :class="['pi font-bold text-2xl! pr-1', store.growth > 0 ? 'text-green-500 pi-arrow-up' : 'text-red-500 pi-arrow-down']"></i>
                        <div class="text-2xl">${{ store.totalValue }}</div>
                        <span :class="['font-medium text-base ml-2', store.growth > 0 ? 'text-green-500' : 'text-red-500']">{{ store.growth > 0 ? '+' : '' }}{{ store.growth }}%</span>
                    </div>
                </div>
                <Chart v-if="storeData[store.id].value" type="line" :data="storeData[store.id].value" :options="chartOptions" />
            </div>
        </div>
    </div>
</template>
