<script setup>
import { ref } from 'vue';

const props = defineProps({
    dailyTasks: {
        type: Array,
        default: null
    }
});

let completeTask = ref(1);

function changeChecked() {
    completeTask.value = props.dailyTasks.filter((task) => task.checked).length;
}
</script>

<template>
    <div class="col-span-12 md:col-span-4">
        <div class="flex flex-col gap-4 rounded-md border h-full border-surface py-6">
            <div class="flex justify-between items-center mx-6">
                <div class="flex items-center gap-4">
                    <div>
                        <Knob :showValue="false" :size="36" rangeColor="#EEEEEE" readonly :max="5" v-model="completeTask" />
                    </div>
                    <div class="flex flex-col justify-between gap-1">
                        <span class="font-bold text-surface-900 dark:text-surface-0">My Daily Tasks</span>
                        <span class="text-muted-color text-sm"
                            ><span class="font-bold">{{ completeTask }}</span
                            >/5 Tasks</span
                        >
                    </div>
                </div>
                <div>
                    <Button icon="pi pi-plus" label="New Task" outlined></Button>
                </div>
            </div>
            <div class="flex flex-col gap-2 h-[21rem] overflow-auto -mb-6">
                <div v-for="task in dailyTasks" :key="task.id" class="flex justify-between p-4 bg-surface-50 dark:bg-surface-800 cursor-pointer text-muted-color rounded-md mx-6 hover:bg-surface-0 dark:hover:bg-surface-900 hover:shadow">
                    <div class="flex gap-4">
                        <div>
                            <Checkbox @change="changeChecked()" v-model="task.checked" :binary="true"></Checkbox>
                        </div>
                        <div class="flex flex-col gap-2">
                            <span class="font-medium text-sm">{{ task.label }}</span>
                            <div class="flex gap-2 items-center">
                                <i class="pi pi-align-left text-muted-color"></i>
                                <i class="pi pi-file text-muted-color"></i>
                                <i class="pi pi-image text-muted-color"></i>
                            </div>
                        </div>
                    </div>
                    <div class="flex gap-4">
                        <div class="flex items-end">
                            <AvatarGroup>
                                <Avatar :image="task.avatar" shape="circle"></Avatar>
                                <Avatar label="+2" shape="circle" class="bg-surface-200 dark:bg-surface-600 text-muted-color"></Avatar>
                            </AvatarGroup>
                        </div>
                        <div class="flex items-center">
                            <i class="pi pi-ellipsis-h text-muted-color"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
