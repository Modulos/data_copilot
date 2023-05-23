<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRoute } from 'vue-router';
// eslint-disable-next-line import/no-cycle
import useChatsStore from '@/stores/chats';

import ChatInput from '@/components/Chat/ChatInput.vue';
import ChatWelcome from '@/components/Chat/ChatWelcome.vue';
import ModulosFooter from '@/components/ModulosFooter.vue';

const buttonMessage = ref('');
const chatStore = useChatsStore();
const route = useRoute();

function inputMessage(text: string) {
  buttonMessage.value = text;
}

watch(
  () => chatStore.chats,
  async (newValue) => {
    if (newValue.length) {
      if (typeof route.params.id === 'string') {
        chatStore.activeChat = route.params.id;
        await chatStore.getActiveDatasetNameAndArtifactVersion();
      }
    }
  },
  {
    deep: true,
  },
);
</script>

<template>
  <div
    ref="scrollable"
    class="page__wrapp relative w-full transition-width flex flex-col overflow-hidden items-stretch"
  >
    <div class="h-full overflow-y-auto">
      <div class="h-full flex flex-col items-center text-sm pb-10">
        <ChatWelcome @input-message="inputMessage" :welcome-page="false" />
        <ChatInput :text="buttonMessage" class="w-full" />
        <ModulosFooter />
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped></style>

<style lang="scss" scoped>
.page__wrapp {
  min-height: 100vh;
}
</style>
