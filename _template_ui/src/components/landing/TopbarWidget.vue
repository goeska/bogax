<script setup>
function handleScroll($element) {
    const element = document.getElementById($element);
    if (element) {
        setTimeout(() => {
            element.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' });
        }, 200);
    }
}
</script>

<template>
    <div style="height: 68px; backdrop-filter: blur(17px)" class="flex justify-between items-center z-30 px-8 bg-black/40 top-0 w-full fixed">
        <div>
            <img :draggable="false" src="/layout/images/logo/logo.png" alt="" />
        </div>

        <a class="cursor-pointer block lg:hidden text-white" v-styleclass="{ selector: '@next', hideOnOutsideClick: true, enterFromClass: 'hidden', leaveToClass: 'hidden' }">
            <i class="pi pi-bars text-4xl!"></i>
        </a>

        <div id="menu" class="items-center grow hidden lg:flex absolute lg:static w-full lg:px-0 z-30 shadow lg:shadow-none bg-surface-0 lg:bg-transparent! animate-fadein" style="top: 68px; right: 0%">
            <ul class="list-none p-4 lg:p-0 m-0 ml-auto flex lg:items-center select-none flex-col lg:flex-row cursor-pointer">
                <li>
                    <a class="flex m-0 md:ml-8 px-0 py-4 text-surface-900 lg:text-surface-0 leading-normal" v-styleclass="{ selector: '#menu', enterFromClass: 'hidden', leaveToClass: 'hidden' }">
                        <span>HOME</span>
                    </a>
                </li>
                <li>
                    <a class="flex m-0 md:ml-8 px-0 py-4 text-surface-900 lg:text-surface-0 leading-normal" @click="handleScroll('features')" v-styleclass="{ selector: '#menu', enterFromClass: 'hidden', leaveToClass: 'hidden' }">
                        <span>FEATURES</span>
                    </a>
                </li>
                <li>
                    <a class="flex m-0 md:ml-8 px-0 py-4 text-surface-900 lg:text-surface-0 leading-normal" @click="handleScroll('collaboration')" v-styleclass="{ selector: '#menu', enterFromClass: 'hidden', leaveToClass: 'hidden' }">
                        <span>COLLABORATION</span>
                    </a>
                </li>
                <li>
                    <a class="flex m-0 md:ml-8 px-0 py-4 text-surface-900 lg:text-surface-0 leading-normal" @click="handleScroll('events')" v-styleclass="{ selector: '#menu', enterFromClass: 'hidden', leaveToClass: 'hidden' }">
                        <span>EVENTS</span>
                    </a>
                </li>
                <li>
                    <a class="flex m-0 md:ml-8 px-0 py-4 text-surface-900 lg:text-surface-0 leading-normal" @click="handleScroll('video')" v-styleclass="{ selector: '#menu', enterFromClass: 'hidden', leaveToClass: 'hidden' }">
                        <span>VIDEO</span>
                    </a>
                </li>
                <li>
                    <Button class="bg-surface-900! text-surface-0! border-surface-900! m-0! mt-4! md:mt-0! md:ml-8! rounded-md px-3! py-2! font-medium" v-styleclass="{ selector: '#menu', enterFromClass: 'hidden', leaveToClass: 'hidden' }"
                        >LET'S TRY
                    </Button>
                </li>
            </ul>
        </div>
    </div>
</template>
