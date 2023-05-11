<script setup lang="ts">
import { watch } from 'vue';
import { useRouter } from 'vue-router';
import useMessagesStore from '@/stores/messages';
import useChatsStore from '@/stores/chats';
import useBreakpoints from '@/hooks/useBreakpoints';

import SideBarButton from '@/components/SideBar/SideBarButton.vue';
import IconChatBubble from '@/components/icons/IconChatBubble.vue';

const router = useRouter();
const messageStore = useMessagesStore();
const chatStore = useChatsStore();
const { isMobile } = useBreakpoints();

const props = defineProps<{
  title: string;
  chatId: string;
}>();

const openChat = async () => {
  chatStore.activeChat = props.chatId;
  await chatStore.getActiveDatasetNameAndArtifactVersion();
  await messageStore.getMessages(chatStore.activeChat);
  if (messageStore.hasMessages) {
    router.push(`/chat/${props.chatId}`);
  } else {
    router.push(`/chat-welcome/${props.chatId}`);
  }
};

watch(
  () => chatStore.activeChat,
  () => {
    messageStore.clearMessages();
  },
);
</script>

<template>
  <SideBarButton
    :id="chatId"
    :active="chatId === chatStore.activeChat"
    :description="props.title"
    :hasActions="true"
    :canBeInput="true"
    @clicked="openChat"
  >
    <template #icon>
      <IconChatBubble class="w-5 h-5 fill-gray-200" :class="[isMobile ? 'mr-2' : '']" />
    </template>
  </SideBarButton>
</template>
