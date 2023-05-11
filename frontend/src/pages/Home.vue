<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
// eslint-disable-next-line import/no-cycle
import useArtifactStore from '@/stores/artifacts';
import useBreakpoints from '@/hooks/useBreakpoints';
import { useRoute } from 'vue-router';

import ChatInput from '@/components/Chat/ChatInput.vue';
import ChatWelcome from '@/components/Chat/ChatWelcome.vue';
import ModulosFooter from '@/components/ModulosFooter.vue';

const route = useRoute();
const artifactsStore = useArtifactStore();
const { isMobile } = useBreakpoints();
const buttonMessage = ref('');

function inputMessage(text: string) {
  buttonMessage.value = text;
}

const isMobileHome = computed(() => route.name === 'home' && isMobile);

onMounted(() => {
  artifactsStore.getArtifacts();
});
</script>

<template>
  <div
    ref="scrollable"
    class="page__wrapp relative w-full transition-width flex flex-col overflow-hidden items-stretch"
  >
    <div class="h-full overflow-y-auto">
      <div class="h-full flex flex-col items-center text-sm">
        <ChatWelcome @input-message="inputMessage" />
        <ChatInput v-if="!isMobileHome" :text="buttonMessage" class="w-full" />
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
