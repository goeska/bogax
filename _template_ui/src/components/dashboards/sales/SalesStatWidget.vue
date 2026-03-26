<script setup>
import { useLayout } from '@/layout/composables/layout';
import { onMounted, ref, watch } from 'vue';

const stats = ref([
    {
        icon: 'pi pi-shopping-cart',
        title: 'Orders',
        value: '640',
        subValue: '1420 Completed',
        colorClass: 'text-teal-600 dark:text-teal-200'
    },
    {
        icon: 'pi pi-dollar',
        title: 'Revenue',
        value: '$57K',
        subValue: '$9,640 Income',
        colorClass: 'text-teal-600 dark:text-teal-200'
    },
    {
        icon: 'pi pi-users',
        title: 'Customers',
        value: '8572',
        subValue: '25402 Registered',
        colorClass: 'text-pink-600 dark:text-pink-200'
    },
    {
        icon: 'pi pi-comments',
        title: 'Comments',
        value: '805',
        subValue: '85 Responded',
        colorClass: 'text-teal-600 dark:text-teal-200'
    }
]);

const { isDarkTheme } = useLayout();
const menu1 = ref(null);
const menu2 = ref(null);
const menu3 = ref(null);
const menu4 = ref(null);

const items = ref([
    { label: 'Update', icon: 'pi pi-fw pi-refresh' },
    { label: 'Edit', icon: 'pi pi-fw pi-pencil' }
]);

const chartDatasets = ref([
    [50, 64, 32, 24, 18, 27, 20, 36, 30],
    [11, 30, 52, 35, 39, 20, 14, 18, 29],
    [20, 29, 39, 36, 45, 24, 28, 20, 15],
    [30, 39, 50, 21, 33, 18, 10, 24, 20]
]);

const menuRefs = [menu1, menu2, menu3, menu4];

const createChartData = (data) => ({
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'],
    datasets: [
        {
            data,
            borderColor: ['#4DD0E1'],
            backgroundColor: ['rgba(77, 208, 225, 0.8)'],
            borderWidth: 2,
            fill: true,
            tension: 0.4
        }
    ]
});

const chartOptions = {
    plugins: {
        legend: {
            display: false
        }
    },
    responsive: true,
    scales: {
        y: {
            display: false
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
    }
};

const overviewChartData1 = ref(createChartData(chartDatasets.value[0]));
const overviewChartData2 = ref(createChartData(chartDatasets.value[1]));
const overviewChartData3 = ref(createChartData(chartDatasets.value[2]));
const overviewChartData4 = ref(createChartData(chartDatasets.value[3]));

const overviewChartOptions1 = ref(chartOptions);
const overviewChartOptions2 = ref(chartOptions);
const overviewChartOptions3 = ref(chartOptions);
const overviewChartOptions4 = ref(chartOptions);

function toggleMenu(event, menuRef) {
    menuRef.value.toggle(event);
}

function refreshChart() {
    setOverviewColors();
}

function setOverviewColors() {
    const colors = getOverviewColors();
    const chartData = [overviewChartData1, overviewChartData2, overviewChartData3, overviewChartData4];

    chartData.forEach((chart, index) => {
        const isPink = index === 2;
        chart.value.datasets[0].borderColor[0] = isPink ? colors.pinkBorderColor : colors.tealBorderColor;
        chart.value.datasets[0].backgroundColor[0] = isPink ? colors.pinkBgColor : colors.tealBgColor;
    });
}

function getOverviewColors() {
    return {
        pinkBorderColor: !isDarkTheme.value ? '#E91E63' : '#EC407A',
        pinkBgColor: !isDarkTheme.value ? '#F48FB1' : '#F8BBD0',
        tealBorderColor: !isDarkTheme.value ? '#009688' : '#26A69A',
        tealBgColor: !isDarkTheme.value ? '#80CBC4' : '#B2DFDB'
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
    <template v-for="(stat, index) in stats" :key="index">
        <div class="col-span-12 md:col-span-6 lg:col-span-3">
            <div class="card flex flex-col">
                <div class="flex items-center text-gray-700">
                    <i :class="stat.icon" class="text-color"></i>
                    <span class="font-semibold m-0 text-color pl-2">{{ stat.title }}</span>
                    <div class="ml-auto">
                        <Button icon="pi pi-ellipsis-h" rounded text @click="toggleMenu($event, menuRefs[index])"></Button>
                        <Menu :ref="(el) => (menuRefs[index].value = el)" popup :model="items"></Menu>
                    </div>
                </div>
                <div class="flex justify-between mt-4 flex-wrap">
                    <div class="flex flex-col" style="width: 80px">
                        <span class="mb-1 text-4xl">{{ stat.value }}</span>
                        <span class="font-medium rounded-sm p-1 text-sm" :class="stat.colorClass">{{ stat.subValue }}</span>
                    </div>
                    <div class="flex items-end">
                        <Chart
                            type="line"
                            :data="index === 0 ? overviewChartData1 : index === 1 ? overviewChartData2 : index === 2 ? overviewChartData3 : overviewChartData4"
                            :options="index === 0 ? overviewChartOptions1 : index === 1 ? overviewChartOptions2 : index === 2 ? overviewChartOptions3 : overviewChartOptions4"
                            :height="60"
                            :width="160"
                        >
                        </Chart>
                    </div>
                </div>
            </div>
        </div>
    </template>
</template>
