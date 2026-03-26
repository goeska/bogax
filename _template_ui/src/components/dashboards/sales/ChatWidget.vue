<script setup>
import { nextTick, ref } from 'vue';

const menu = ref(null);
const op = ref(null);
const chatInput = ref('');

const items = ref([
    { label: 'View Media', icon: 'pi pi-fw pi-images' },
    { label: 'Starred Messages', icon: 'pi pi-fw pi-star' },
    { label: 'Search', icon: 'pi pi-fw pi-search' }
]);

const chatMessages = ref([
    { from: 'Ioni Bowcher', url: '/demo/images/avatar/ionibowcher.png', messages: ['Hey M. hope you are well.', 'Our idea is accepted by the board. Now it’s time to execute it'] },
    { messages: ['We did it! 🤠'] },
    { from: 'Ioni Bowcher', url: '/demo/images/avatar/ionibowcher.png', messages: ["That's really good!"] },
    { messages: ['But it’s important to ship MVP ASAP'] },
    { from: 'Ioni Bowcher', url: '/demo/images/avatar/ionibowcher.png', messages: ['I’ll be looking at the process then, just to be sure 🤓'] },
    { messages: ['That’s awesome. Thanks!'] }
]);

const chatEmojis = ref([
    '😀',
    '😃',
    '😄',
    '😁',
    '😆',
    '😅',
    '😂',
    '🤣',
    '😇',
    '😉',
    '😊',
    '🙂',
    '🙃',
    '😋',
    '😌',
    '😍',
    '🥰',
    '😘',
    '😗',
    '😙',
    '😚',
    '🤪',
    '😜',
    '😝',
    '😛',
    '🤑',
    '😎',
    '🤓',
    '🧐',
    '🤠',
    '🥳',
    '🤗',
    '🤡',
    '😏',
    '😶',
    '😐',
    '😑',
    '😒',
    '🙄',
    '🤨',
    '🤔',
    '🤫',
    '🤭',
    '🤥',
    '😳',
    '😞',
    '😟',
    '😠',
    '😡',
    '🤬',
    '😔',
    '😟',
    '😠',
    '😡',
    '🤬',
    '😔',
    '😕',
    '🙁',
    '😬',
    '🥺',
    '😣',
    '😖',
    '😫',
    '😩',
    '🥱',
    '😤',
    '😮',
    '😱',
    '😨',
    '😰',
    '😯',
    '😦',
    '😧',
    '😢',
    '😥',
    '😪',
    '🤤'
]);

function toggleMenu(event) {
    menu.value.toggle(event);
}

function toggleEmojis(event) {
    op.value.toggle(event);
}

async function onChatKeydown(event) {
    if (event.key === 'Enter') {
        const message = event.target.value;
        const lastMessage = chatMessages.value[chatMessages.value.length - 1];

        if (lastMessage.from) {
            chatMessages.value.push({
                self: true,
                from: 'Jerome Bell',
                url: '/demo/images/avatar/ivanmagalhaes.png',
                messages: [message]
            });
        } else {
            lastMessage.messages.push(message);
        }

        if (message.match(/primeng|primereact|primefaces|primevue/i)) {
            chatMessages.value.push({
                nth: false,
                from: 'Ioni Bowcher',
                url: '/demo/images/avatar/ionibowcher.png',
                messages: ['Always bet on Prime!']
            });
        }

        event.target.value = '';

        await nextTick();
        const chatContainer = document.querySelector('.chat-container');
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }
}

function onEmojiOverlayPanel(chatInput, emoji) {
    op.value.hide();
    onEmojiClick(chatInput, emoji);
}

function onEmojiClick(emoji) {
    chatInput.value += emoji;
}
</script>

<template>
    <div class="card h-full">
        <div class="flex items-center justify-between mb-4">
            <span class="font-semibold text-xl m-0">Chat</span>
            <div>
                <Button icon="pi pi-ellipsis-h" class="mb-1 mr-2" rounded text plain @click="toggleMenu"></Button>
                <Menu ref="menu" popup :model="items"> </Menu>
            </div>
        </div>
        <div>
            <ul class="chat-container m-0 px-4 pt-4 pb-0 border-0 list-none h-[30rem] overflow-y-auto outline-0" ref="chatcontainer">
                <li
                    v-for="(chartMessage, index) in chatMessages"
                    :key="index"
                    class="flex items-start"
                    :class="{ from: !!chartMessage.from, 'text-right justify-end': !chartMessage.from, 'mb-3': index !== chatMessages.length - 1, 'mb-1': index === chatMessages.length - 1 }"
                >
                    <img v-if="!!chartMessage.url" :src="chartMessage.url" alt="avatar" :width="32" class="mr-2" />
                    <div
                        class="flex flex-col"
                        :class="{
                            'items-start': !!chartMessage.from,
                            'items-end': !chartMessage.from
                        }"
                    >
                        <span
                            style="word-break: break-word"
                            v-for="(message, j) in chartMessage.messages"
                            :key="j"
                            class="p-4 rounded-3xl text-white"
                            :class="{
                                'bg-cyan-500': !!chartMessage.from,
                                'bg-pink-500': !chartMessage.from,
                                'mt-1': j !== 0
                            }"
                        >
                            {{ message }}
                        </span>
                    </div>
                </li>
            </ul>
            <InputGroup class="mt-4">
                <InputGroupAddon>
                    <Button icon="pi pi-plus-circle" class="h-full" severity="secondary"></Button>
                </InputGroupAddon>
                <InputText ref="input" v-model="chatInput" placeholder="Write your message (Hint: 'PrimeVue')" @keydown="onChatKeydown($event)" />
                <InputGroupAddon>
                    <Button icon="pi pi-video" class="h-full" severity="secondary"></Button>
                </InputGroupAddon>
                <InputGroupAddon>
                    <Button icon="pi pi-clock" @click="toggleEmojis" class="h-full" severity="secondary"></Button>
                    <Popover ref="op" class="emoji" style="width: 45em">
                        <Button type="button" v-for="emoji in chatEmojis" :key="emoji" @click="onEmojiOverlayPanel(emoji)" :label="emoji" class="emoji-button p-2" text plain></Button>
                    </Popover>
                </InputGroupAddon>
            </InputGroup>
        </div>
    </div>
</template>
