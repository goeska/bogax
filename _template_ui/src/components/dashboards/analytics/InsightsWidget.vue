<script setup>
import { useLayout } from '@/layout/composables/layout';
import { onMounted, ref, watch } from 'vue';

const { isDarkTheme } = useLayout();

const menuRef = ref(null);
const doughnutRef = ref(null);
const doughnutData = ref(null);
const doughnutOptions = ref(null);

const items = ref([
    { label: 'Update', icon: 'pi pi-fw pi-refresh' },
    { label: 'Edit', icon: 'pi pi-fw pi-pencil' }
]);

const documentStyle = getComputedStyle(document.documentElement);

const colorKeys = ['indigo', 'blue', 'cyan', 'green', 'emerald', 'orange', 'yellow'];

function toggleMenu(event) {
    menuRef.value.toggle(event);
}

function changeDoughnutDataView() {
    if (doughnutRef.value.chart.config.options.circumference === 360) {
        doughnutRef.value.chart.config.options.circumference = 180;
        doughnutRef.value.chart.config.options.rotation = -1 * 90;
    } else {
        doughnutRef.value.chart.config.options.circumference = 360;
        doughnutRef.value.chart.config.options.rotation = 0;
    }

    doughnutRef.value.chart.update();
}

function getDoughnutData() {
    const borderColor = getComputedStyle(document.body).getPropertyValue('--surface-border') || 'rgba(160, 167, 181, .3)';
    const suffix = isDarkTheme.value ? '400' : '500';
    const backgroundColor = colorKeys.map((color) => documentStyle.getPropertyValue(`--p-${color}-${suffix}`));

    return {
        labels: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        datasets: [
            {
                data: [11, 29, 71, 33, 28, 95, 6],
                backgroundColor,
                borderColor
            }
        ]
    };
}

function getDoughnutOptions() {
    const textColor = getComputedStyle(document.body).getPropertyValue('--text-color') || 'rgba(0, 0, 0, 0.87)';
    const fontFamily = getComputedStyle(document.body).getPropertyValue('--font-family');

    return {
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        family: fontFamily
                    },
                    color: textColor
                }
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        circumference: 180,
        rotation: -90,
        animation: {
            animateScale: true,
            animateRotate: true
        }
    };
}

function refreshChart() {
    doughnutData.value = getDoughnutData();
    doughnutOptions.value = getDoughnutOptions();
}

onMounted(refreshChart);
watch(() => isDarkTheme.value, refreshChart);
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-2">
            <span class="text-xl font-semibold m-0">Insights</span>
            <div>
                <Button icon="pi pi-ellipsis-h" rounded text plain @click="toggleMenu" />
                <Menu ref="menuRef" popup :model="items" />
            </div>
        </div>
        <div class="border-b border-surface text-sm text-muted-color mb-2 flex items-center">
            <span>November 22 - November 29</span>
            <Button label="Semi/Full Data" class="ml-auto" text @click="changeDoughnutDataView" />
        </div>
        <Chart ref="doughnutRef" type="doughnut" :data="doughnutData" :options="doughnutOptions" :height="200" />
        <div class="flex flex-col justify-center">
            <div class="flex flex-row items-center mt-6 px-4">
                <i class="pi pi-thumbs-up p-4 rounded-full bg-green-500 text-white"></i>
                <div class="flex flex-col ml-4">
                    <span>Best Day of the Week</span>
                    <small>Friday</small>
                </div>
                <span class="text-indigo-500 ml-auto">95</span>
            </div>
            <div class="flex flex-row items-center my-6 px-4">
                <i class="pi pi-thumbs-down rounded-full p-4 bg-orange-500 text-white"></i>
                <div class="flex flex-col ml-4">
                    <span>Worst Day of the Week</span>
                    <small>Saturday</small>
                </div>
                <span class="text-indigo-500 ml-auto">6</span>
            </div>
        </div>
    </div>
</template>
