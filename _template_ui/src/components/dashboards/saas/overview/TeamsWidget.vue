<script setup>
import { ref } from 'vue';

const emit = defineEmits(['change:filteredTeamMembers']);

const props = defineProps({
    selectedTeam: String
});

const teams = ref([
    {
        title: 'UX Researchers',
        avatar: ['/demo/images/avatar/circle/avatar-f-1.png', '/demo/images/avatar/circle/avatar-f-6.png', '/demo/images/avatar/circle/avatar-f-11.png', '/demo/images/avatar/circle/avatar-f-12.png'],
        avatarText: '+4',
        badgeClass: 'bg-pink-500'
    },
    {
        title: 'UX Designers',
        avatar: ['/demo/images/avatar/circle/avatar-f-2.png'],
        badgeClass: 'bg-blue-500'
    },
    {
        title: 'UI Designers',
        avatar: ['/demo/images/avatar/circle/avatar-f-3.png', '/demo/images/avatar/circle/avatar-f-8.png'],
        avatarText: '+1',
        badgeClass: 'bg-green-500'
    },
    {
        title: 'Front-End Developers',
        avatar: ['/demo/images/avatar/circle/avatar-f-4.png', '/demo/images/avatar/circle/avatar-f-9.png'],
        badgeClass: 'bg-yellow-500'
    },
    {
        title: 'Back-End Developers',
        avatar: ['/demo/images/avatar/circle/avatar-f-10.png'],
        badgeClass: 'bg-purple-500'
    }
]);

function teamFilter(team) {
    emit('change:filteredTeamMembers', team);
}
</script>

<template>
    <div class="col-span-12 md:col-span-4">
        <div class="border border-surface p-4 rounded-md flex flex-col gap-4">
            <div class="flex justify-between items-center">
                <div class="flex flex-col gap-1">
                    <span class="font-semibold text-surface-900 dark:text-surface-0 text-lg">Teams</span>
                    <span class="text-sm text-muted-color">18 Members</span>
                </div>
                <Button label="New Team" icon="pi pi-users"></Button>
            </div>
            <div class="flex flex-col gap-1">
                <div
                    v-for="team in teams"
                    :key="team.title"
                    @click="teamFilter(team.title)"
                    class="flex justify-between items-center border border-transparent rounded-md p-4 -mx-2 cursor-pointer hover:bg-emphasis"
                    :class="{
                        'bg-primary-50 border-primary-100 dark:bg-primary-900': props.selectedTeam === team.title
                    }"
                >
                    <div class="flex items-center gap-4 min-w-0">
                        <div :style="{ width: '7px', height: '7px' }" class="shrink-0 rounded-full" :class="team.badgeClass"></div>
                        <span class="truncate">{{ team.title }}</span>
                    </div>
                    <div class="flex gap-2 items-center">
                        <AvatarGroup>
                            <Avatar v-for="avatar in team.avatar" :key="avatar" :image="avatar" shape="circle"></Avatar>
                            <Avatar v-if="team.avatarText" :label="team.avatarText" shape="circle" class="bg-surface-200 dark:bg-surface-600 text-muted-color" style="color: #ffffff"></Avatar>
                        </AvatarGroup>
                        <i v-if="props.selectedTeam === team.title" class="pi pi-chevron-right text-primary"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
