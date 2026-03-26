<script setup>
import StatWidget from '@/components/dashboards/analytics/AnalyticsStatWidget.vue';
import TableWidget from '@/components/dashboards/analytics/AnalyticsTableWidget.vue';
import ExpensesWidget from '@/components/dashboards/analytics/ExpensesWidget.vue';
import InsightsWidget from '@/components/dashboards/analytics/InsightsWidget.vue';
import MonthlyComparisonWidget from '@/components/dashboards/analytics/MonthlyComparisonWidget.vue';
import RatingsWidget from '@/components/dashboards/analytics/RatingsWidget.vue';
import StoresWidget from '@/components/dashboards/analytics/StoresWidget.vue';
import TopSearchesWidget from '@/components/dashboards/analytics/TopSearchesWidget.vue';
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <div class="col-span-12 md:col-span-8">
            <MonthlyComparisonWidget />
        </div>
        <div class="col-span-12 md:col-span-4">
            <InsightsWidget />
        </div>
        <StatWidget />
        <div class="col-span-12 md:col-span-12">
            <StoresWidget />
        </div>
        <div class="col-span-12 md:col-span-6">
            <TopSearchesWidget />
        </div>
        <div class="col-span-12 md:col-span-6">
            <TableWidget />
        </div>
        <div class="col-span-12 md:col-span-4">
            <ExpensesWidget />
        </div>
        <div class="col-span-12 md:col-span-8">
            <RatingsWidget />
        </div>
    </div>
</template>
