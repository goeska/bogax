<script setup>
import IntroduceWidget from '@/components/dashboards/saas/IntroduceWidget.vue';
import ProjectOverviewWidget from '@/components/dashboards/saas/overview/ProjectOverviewWidget.vue';
import UpgradeWidget from '@/components/dashboards/saas/UpgradeWidget.vue';
import MyWorkspaceWidget from '@/components/dashboards/saas/workspace/MyWorkspaceWidget.vue';
</script>

<template>
    <div class="grid grid-cols-12 gap-8 mt-1">
        <div class="col-span-12 md:col-span-8">
            <IntroduceWidget />
        </div>
        <div class="col-span-12 md:col-span-4">
            <UpgradeWidget />
        </div>
        <div class="col-span-12">
            <MyWorkspaceWidget />
        </div>
        <div class="col-span-12">
            <ProjectOverviewWidget />
        </div>
    </div>
</template>
