<script setup>
import { useLayout } from '@/layout/composables/layout';
import { onMounted, ref, watch } from 'vue';

const { isDarkTheme } = useLayout();

const menu = ref(null);

const items = ref([
    { label: 'Update', icon: 'pi pi-fw pi-refresh' },
    { label: 'Edit', icon: 'pi pi-fw pi-pencil' }
]);

const ordersOptions = ref(null);
const ordersChart = ref({
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'],
    datasets: [
        {
            label: 'New Orders',
            data: [31, 23, 69, 29, 62, 25, 59, 26, 46],
            borderColor: ['#4DD0E1'],
            backgroundColor: ['rgba(77, 208, 225, 0.2)'],
            borderWidth: 2,
            fill: true,
            tension: 0.4
        },
        {
            label: 'Completed Orders',
            data: [57, 48, 27, 88, 38, 3, 22, 60, 56],
            borderColor: ['#3F51B5'],
            backgroundColor: ['rgba(63, 81, 181, 0.4)'],
            borderWidth: 2,
            fill: false,
            tension: 0.4
        }
    ]
});

function toggleMenu(event) {
    menu.value.toggle(event);
}

function refreshChart() {
    ordersOptions.value = getOrdersOptions();
}

function getOrdersOptions() {
    const textColor = getComputedStyle(document.body).getPropertyValue('--text-color') || 'rgba(0, 0, 0, 0.87)';
    const gridLinesColor = getComputedStyle(document.body).getPropertyValue('--surface-border') || 'rgba(160, 167, 181, .3)';
    const fontFamily = getComputedStyle(document.body).getPropertyValue('--font-family');

    return {
        plugins: {
            legend: {
                display: true,
                labels: {
                    font: {
                        family: fontFamily
                    },
                    color: textColor
                }
            }
        },
        maintainAspectRatio: false,
        responsive: true,
        scales: {
            y: {
                ticks: {
                    font: {
                        family: fontFamily
                    },
                    color: textColor
                },
                grid: {
                    color: gridLinesColor
                }
            },
            x: {
                ticks: {
                    font: {
                        family: fontFamily
                    },
                    color: textColor
                },
                grid: {
                    color: gridLinesColor
                }
            }
        }
    };
}

onMounted(() => {
    refreshChart();
});

watch([isDarkTheme], () => {
    refreshChart();
});
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="font-semibold text-xl m-0">Order Graph</span>
            <div>
                <Button icon="pi pi-ellipsis-h" rounded text plain @click="toggleMenu"></Button>
                <Menu ref="menu" popup :model="items"> </Menu>
            </div>
        </div>
        <Chart type="line" :data="ordersChart" :options="ordersOptions" :height="375" :width="300"></Chart>
    </div>
</template>
