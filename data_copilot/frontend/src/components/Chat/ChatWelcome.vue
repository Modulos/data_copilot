<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';

import useChatsStore from '@/stores/chats';
import { useAuthStore } from '@/stores/auth';
import useBreakpoints from '@/hooks/useBreakpoints';

import LogoLanding from '@/assets/icons/svg/logo-landing.svg?component';

import SelectModal from '@/components/ui/SelectModal.vue';
import MessageButton from '@/components/ui/MessageButton.vue';
import ChatFileSelect from './ChatFileSelect.vue';
import ChatFileUpload from './ChatFileUpload.vue';

const emit = defineEmits(['inputMessage']);

const route = useRoute();
const chatStore = useChatsStore();
const auth = useAuthStore();
const { isMobile } = useBreakpoints();

const isMobileHome = computed(() => route.name === 'home' && isMobile);

const isModalOpen = ref(false);
const showContent = route.name === 'home' && auth.activateAnimation ? ref(false) : ref(true);
const showLogo = route.name === 'home' && auth.activateAnimation ? ref(false) : ref(true);

function inputMessage(text: string) {
  emit('inputMessage', text);
}

onMounted(() => {
  setTimeout(() => {
    showLogo.value = true;
  }, 500);
  setTimeout(() => {
    showContent.value = true;
  }, 1300);
});
</script>

<template>
  <div
    class="chat__wrapp flex flex-col items-center text-sm w-full"
    :style="{ 'padding-bottom': isMobileHome ? '200px' : '300px' }">
    <LogoLanding class="logo" :class="[!showLogo ? 'logo-start' : '']" />
    <div
      class="content__wrapp text-gray-800 w-full md:max-w-2xl lg:max-w-3xl md:h-full md:flex md:flex-col"
      :class="[showContent ? 'show-content' : '']">
      <div class="description">
        <span>
          DataCopilot serves as a robust framework for building your
          own prompt-based applications, enhancing user experience and
          interaction.
        </span>
      </div>
      <div
        v-if="route.name === 'chat-welcome' && !chatStore.isLoading"
        class="messages__container justify-between"
        :class="[isMobile ? 'flex-column' : 'flex']">
        <MessageButton @input-message="inputMessage" :text="'What are the names of the columns in my data?'" />
        <MessageButton @input-message="inputMessage" :text="'Compute the mean of all numeric columns'" />
        <MessageButton @input-message="inputMessage" :text="'Compute the standard deviation of all columns'" />
      </div>
      <div
        v-if="route.name === 'home' && !chatStore.isLoading"
        class="uploads__container flex flex-col lg:flex lg:flex-row">
        <ChatFileUpload class="my-3" :class="[isMobile ? 'mx-0' : 'mx-5']" />
        <ChatFileSelect class="my-3" :class="[isMobile ? 'mx-0' : 'mx-5']" @click="isModalOpen = true" />
      </div>
    </div>
    <SelectModal class="select-modal" :class="[isModalOpen ? '' : 'hidden']" @close-modal="isModalOpen = false" />
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.chat__wrapp {
  padding-top: 200px;

  @media screen and (max-width:600px) {
    padding-top: 150px;
  }

  .logo {
    width: 542px;
    height: 105px;
    margin: 0 auto;
    position: absolute;
    top: 125px;
    left: 50%;
    transform: translate(-50%, -50%) scale(1);
    transition: all 0.5s ease;

    @media screen and (max-width:600px) {
      width: unset;
      height: unset;
      top: 7%;
      left: -35%;
      transform: translate(0, 0) scale(0.55);

    }
  }

  .logo-start {
    position: absolute;
    top: 50%;
    transform: translate(-50%, -50%) scale(1.5);

    @media screen and (max-width:600px) {
      top: 40%;
      left: -35%;
      transform: translate(0, 0) scale(0.59);
    }
  }

  .content__wrapp {
    transition: all 0.4s ease;
    opacity: 0;

    .description {
      @include Inter(16px, 28px);
      max-width: 560px;
      font-weight: 400;
      text-align: center;
      margin: 36px auto 85px;

      @media screen and (max-width:600px) {
        @include Inter(14px, 24px);
        margin: 30px auto 70px;
      }

      span {
        opacity: 0.6;
      }

      .white {
        opacity: 1;
        margin: 0 3px;
        font-weight: bold;
      }
    }
  }

  .show-content {
    opacity: 1;
  }

  // .messages__container {
  //   margin-bottom: 70px;
  // }
  // .uploads__container {
  //   margin-bottom: 70px;
  // }
  .select-modal {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
  }
}
</style>
