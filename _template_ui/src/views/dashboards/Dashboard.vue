<script setup>
import ActivityWidget from '@/components/dashboards/sales/ActivityWidget.vue';
import BestSellersWidget from '@/components/dashboards/sales/BestSellersWidget.vue';
import ChatWidget from '@/components/dashboards/sales/ChatWidget.vue';
import ContactWidget from '@/components/dashboards/sales/ContactWidget.vue';
import CustomTimelineWidget from '@/components/dashboards/sales/CustomTimelineWidget.vue';
import OrderGraphWidget from '@/components/dashboards/sales/OrderGraphWidget.vue';
import StatsWidget from '@/components/dashboards/sales/SalesStatWidget.vue';
import TableWidget from '@/components/dashboards/sales/SalesTableWidget.vue';
</script>

<template>
    <div class="grid grid-cols-12 gap-8">
        <StatsWidget />
        <div class="col-span-12 lg:col-span-6">
            <ContactWidget />
        </div>
        <div class="col-span-12 lg:col-span-6">
            <OrderGraphWidget />
        </div>
        <div class="col-span-12 lg:col-span-6">
            <CustomTimelineWidget />
        </div>
        <div class="col-span-12 md:col-span-12 lg:col-span-6">
            <TableWidget />
        </div>
        <div class="col-span-12 lg:col-span-6">
            <ChatWidget />
        </div>
        <div class="col-span-12 lg:col-span-3">
            <ActivityWidget />
        </div>
        <div class="col-span-12 lg:col-span-3">
            <BestSellersWidget />
        </div>
    </div>
</template>
