<script setup lang="ts">
import {
  ref, watch, onMounted,
} from 'vue';
import { useRouter, useRoute } from 'vue-router';
import useMessagesStore from '@/stores/messages';
import useChatsStore from '@/stores/chats';
import { useAuthStore } from '@/stores/auth';
import useBreakpoints from '@/hooks/useBreakpoints';

import IconSend from '@/components/icons/IconSend.vue';
import MessageIcon from '@/assets/icons/svg/chat_bubble.svg?component';
import Close from '@/assets/icons/svg/close.svg?component';

const props = defineProps({
  text: {
    type: String,
    default: '',
  },
  fixed: Boolean,
});

const router = useRouter();
const route = useRoute();

const messages = useMessagesStore();
const chats = useChatsStore();
const auth = useAuthStore();
const { isMobile } = useBreakpoints();

const inputText = ref(props.text);
const showInput = route.name === 'home' && auth.activateAnimation ? ref(false) : ref(true);

const sendMessage = async () => {
  if (
    inputText.value === ''
    || chats.activeChat === null
    || chats.artifactVersionId === null
    || messages.inputDisabled
  ) {
    return;
  }
  const messageId = await messages.postMessage(
    chats.activeChat,
    inputText.value,
    chats.artifactVersionId,
  );
  if (messageId === undefined) {
    return;
  }
  await messages.executeMessage(chats.activeChat, messageId);
  inputText.value = '';

  if (route.name !== 'chat/:id') {
    router.push(`/chat/${chats.activeChat}`);
  }
};

function removeChat() {
  inputText.value = '';
  chats.activeChat = null;
  router.push('/');
}

watch(
  () => props.text,
  (newValue) => {
    inputText.value = newValue;
  },
);

onMounted(() => {
  setTimeout(() => {
    showInput.value = true;
  }, 1500);
});
</script>

<template>
  <div
    class="input__wrapp w-full"
    :class="[fixed ? 'fixed bottom-0' : '', messages.hasMessages && route.name === 'chat/:id' ? 'input-mask' : '', !showInput ? 'hide-input' : '', route.name !== 'chat/:id' ? 'spec-position' : !isMobile ? 'translate-left' : '']">
    <div
      class="text-base gap-4 md:gap-6 m-auto md:max-w-2xl lg:max-w-2xl xl:max-w-3xl md:py-6 flex lg:px-0"
      :class="[isMobile && route.name !== 'chat/:id' ? 'py-4' : 'p-4', !isMobile && route.name === 'chat/:id' ? 'translate-right' : '']"
    >
      <div class="layer w-full">
        <div
          v-if="route.name !== 'home'"
          class="active-chat__container w-full flex items-center"
          :class="[messages.hasMessages && route.name === 'chat/:id' ? 'temporary-shadow' : '']"
        >
          <MessageIcon />
          <span>{{ chats.activeDatasetName }}</span>
          <Close v-if="!messages.hasMessages && route.name !== 'chat/:id'" class="icon-close" @click="removeChat" />
        </div>

        <div
          class="input__container flex align-items-center justify-between w-full py-2 flex-grow md:py-3 md:pl-4 md:pr-4 relative rounded-md shadow-[0_0_10px_rgba(0,0,0,0.10)]"
          :class="[route.name !== 'home' ? 'active__container' : '']"
        >
          <label for="mainInput" />
          <input
            id="mainInput"
            v-on:keyup.enter="sendMessage"
            v-model="inputText"
            :disabled="route.name === 'home' || chats.artifactVersionId === null"
            type="text"
            class="input m-0 resize-none border-0 bg-transparent p-0 pl-2 pr-7 outline-none md:pl-0 w-full"
            placeholder="Ask your question about your dataset here"
          />
          <button
            type="button"
            v-on:click="sendMessage"
            :disabled="route.name === 'home' || messages.inputDisabled || chats.artifactVersionId === null"
            class="p-1 rounded-md text-gray-500 md:bottom-2.5 md:right-2 hover:bg-gray-100 disabled:hover:bg-transparent"
          >
            <IconSend class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.input__wrapp {
  transition: all 0.5s ease;
  .layer {
    position: relative;
    .active-chat__container {
      max-height: 47px;
      background: $green;
      border-radius: 10px 10px 0px 0px;
      padding: 15px 23px;
      position: absolute;
      left: 0;
      top: -42px;
      span {
        @include Inter(16px, 18px);
        color: $dark-blue;
        display: inline-block;
        margin: 0 15px;
      }
      .icon-close {
        cursor: pointer;
      }
    }
    .temporary-shadow {
      box-shadow: 0px -1px 80px black;
    }
    .input__container {
      height: 65px;
      background-color: rgba(43, 46, 132, 0.6);
      border: 1px solid rgba(39, 255, 198, 0.6);
      box-shadow: 0px 0px 15px rgba(0, 0, 0, 0.1);
      border-radius: 6px;

      .input {
        @include Inter(14px, 18px);
        font-weight: 400;
      }
      .input::placeholder {
        @include Inter(14px, 18px);
        font-weight: 400;
        opacity: 0.4;
      }
    }
    .active__container {
      background-color: rgba(43, 46, 132, 1);
      border: 1px solid rgba(39, 255, 198, 1);
    }
  }
}
.hide-input {
  position: absolute;
  margin: 0;
  bottom: -120px;
}
.spec-position {
  position: absolute;
  bottom: 160px;
}

.translate-left {
  transform: translateX(-130px);
}

.translate-right {
  transform: translateX(130px);
}

.input-mask {
  background: linear-gradient(180deg, rgba(9, 21, 117, 0) 0%, #091575 69%);
}

</style>
