<!-- eslint-disable vue/multi-word-component-names -->
<script lang="ts" setup>
import { useRoute } from 'vue-router';
import { ref, watch } from 'vue';
// eslint-disable-next-line import/no-cycle
import useChatsStore from '@/stores/chats';
import useMessagesStore from '@/stores/messages';
import useBreakpoints from '@/hooks/useBreakpoints';
import useScrollUp from '@/composables/useScrollUp';

import LoadingDotsVue from '@/components/ui/LoadingDots.vue';
import ChatInput from '@/components/Chat/ChatInput.vue';
import ChatMessage from '@/components/Chat/ChatMessage.vue';

const chatStore = useChatsStore();
const messageStore = useMessagesStore();
const route = useRoute();
const { isMobile } = useBreakpoints();

const messagesRef = ref<(typeof ChatMessage)[]>([]);

useScrollUp(messageStore.loadMoreMessages, route.params.id);

watch(
  messagesRef,
  () => {
    if (messagesRef.value.length) {
      messagesRef.value[messagesRef.value.length - 1].scrollToElement();
    }
  },
  {
    deep: true,
  },
);

watch(
  () => chatStore.chats,
  async (newValue) => {
    if (newValue.length) {
      if (typeof route.params.id === 'string' && !messageStore.hasMessages) {
        chatStore.activeChat = route.params.id;
        await chatStore.getActiveDatasetNameAndArtifactVersion();
        await messageStore.getMessages(chatStore.activeChat);
      }
    }
  },
  {
    deep: true,
  },
);

</script>

<template>
  <LoadingDotsVue v-if="messageStore.isLoadingMessages" />
  <div
    v-if="!messageStore.isLoading"
    ref="scrollable"
    class="page__wrapp relative w-full transition-width flex flex-col overflow-hidden items-stretch"
  >
    <div class="h-full overflow-y-auto">
      <div class="h-full flex flex-col items-center text-sm">
        <div class="w-full flex flex-col items-center text-sm pb-32" :class="[isMobile ? 'pt-16' : '']">
          <ChatMessage
            v-for="message in messageStore.messages"
            :key="message.id"
            ref="messagesRef"
            :message="message"
          />
          <LoadingDotsVue v-if="messageStore.inputDisabled" />
        </div>
        <ChatInput :fixed="true" class="w-full" />
      </div>
    </div>
  </div>
  <LoadingDotsVue v-else />
</template>

<style lang="scss" scoped>
.page__wrapp {
  min-height: 100vh;
}
</style>
