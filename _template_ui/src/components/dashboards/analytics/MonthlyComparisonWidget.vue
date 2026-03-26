<script setup>
import { useLayout } from '@/layout/composables/layout';
import { onMounted, ref, watch } from 'vue';

const { isDarkTheme } = useLayout();

const chartView = ref(null);
const chartMonthlyData = ref(null);
const chartMonthlyOptions = ref(null);

const documentStyle = getComputedStyle(document.documentElement);

const colorKeys = ['indigo', 'blue', 'cyan', 'teal', 'green', 'emerald', 'lime', 'amber', 'yellow'];

const YEARS_DATA = [
    { year: '2016', data: [6, 25, 47, 12, 7, 70, 42] },
    { year: '2017', data: [81, 3, 5, 11, 59, 47, 99] },
    { year: '2018', data: [68, 47, 46, 46, 61, 70, 94] },
    { year: '2019', data: [31, 9, 18, 76, 6, 11, 79] },
    { year: '2020', data: [85, 37, 47, 29, 2, 10, 54] },
    { year: '2021', data: [28, 48, 40, 19, 86, 27, 90] },
    { year: '2022', data: [89, 18, 75, 18, 97, 61, 54] },
    { year: '2023', data: [18, 36, 39, 58, 41, 50, 72] },
    { year: '2024', data: [31, 4, 35, 74, 47, 35, 46] }
];

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July'];

function getChartMonthlyData() {
    const suffix = isDarkTheme.value ? '400' : '500';
    const colors = colorKeys.map((color) => documentStyle.getPropertyValue(`--p-${color}-${suffix}`));

    return {
        labels: MONTHS,
        datasets: YEARS_DATA.map(({ year, data }, index) => ({
            label: year,
            data,
            borderColor: colors[index],
            backgroundColor: colors[index],
            borderWidth: 2,
            fill: true
        }))
    };
}

function getMonthlyChartOptions() {
    const textColor = getComputedStyle(document.body).getPropertyValue('--text-color') || 'rgba(0, 0, 0, 0.87)';
    const gridLinesColor = getComputedStyle(document.body).getPropertyValue('--surface-border') || 'rgba(160, 167, 181, .3)';
    const fontFamily = getComputedStyle(document.body).getPropertyValue('--font-family');

    const fontConfig = {
        font: { family: fontFamily },
        color: textColor
    };

    return {
        plugins: {
            legend: {
                display: true,
                labels: fontConfig
            }
        },
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'x' },
        scales: {
            y: {
                ticks: fontConfig,
                grid: { color: gridLinesColor }
            },
            x: {
                categoryPercentage: 0.9,
                barPercentage: 0.8,
                ticks: fontConfig,
                grid: { color: gridLinesColor }
            }
        },
        animation: {
            animateScale: true,
            animateRotate: true
        }
    };
}

function changeMonthlyDataView() {
    const { chart } = chartView.value;
    const isStacked = !chart.options.scales.x.stacked;

    chart.options.scales.x.stacked = isStacked;
    chart.options.scales.y.stacked = isStacked;
    chart.update();
}

function refreshChart() {
    chartMonthlyData.value = getChartMonthlyData();
    chartMonthlyOptions.value = getMonthlyChartOptions();
}

onMounted(refreshChart);
watch(() => isDarkTheme.value, refreshChart);
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="text-xl font-semibold m-0">Monthly Comparison</span>
            <Button label="Vertical/Stacked Data" class="ml-auto" text @click="changeMonthlyDataView" />
        </div>

        <Chart ref="chartView" type="bar" :data="chartMonthlyData" :options="chartMonthlyOptions" :height="400" />
    </div>
</template>
