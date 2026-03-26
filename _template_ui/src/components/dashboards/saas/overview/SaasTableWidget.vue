<script setup>
const props = defineProps({
    filteredTeamMembers: {
        type: Array,
        default: null
    }
});
</script>

<template>
    <div class="col-span-12 md:col-span-8">
        <div class="border border-surface rounded-md h-[28rem] overflow-y-auto">
            <div v-for="member in props.filteredTeamMembers" :key="member.avatar" class="grid grid-cols-12 gap-4 grid-nogutter items-center p-4 border-b border-surface text-surface-700 dark:text-surface-100 cursor-pointer hover:text-color">
                <div class="col-span-4">
                    <div class="flex items-center gap-4">
                        <Avatar size="large" shape="circle" :image="member.avatar" class="shrink-0" />
                        <div class="flex flex-col flex-wrap">
                            <span class="font-medium">{{ member.name }}</span>
                            <span class="text-sm">{{ member.title }}</span>
                        </div>
                    </div>
                </div>
                <div class="col-span-6">
                    <div class="flex justify-between gap-8 flex-1">
                        <div class="flex flex-col" style="flex-basis: 100%">
                            <span class="font-medium">{{ member.taskCount }}</span>
                            <span class="text-sm">Task</span>
                        </div>
                        <div class="flex flex-col" style="flex-basis: 100%">
                            <span class="font-medium">{{ member.doneCount }}</span>
                            <span class="text-sm">Done</span>
                        </div>
                        <div class="flex flex-col" style="flex-basis: 100%">
                            <span class="font-medium">{{ member.sprintCount }}</span>
                            <span class="text-sm">Sprint</span>
                        </div>
                        <div class="flex flex-col" style="flex-basis: 100%">
                            <span class="font-medium">{{ member.onProjectsCount }}</span>
                            <span class="text-sm">On Projects</span>
                        </div>
                    </div>
                </div>
                <div class="col-span-2">
                    <div class="flex justify-end">
                        <Button class="text-surface-900 dark:text-surface-0" rounded text icon="pi pi-ellipsis-h" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
