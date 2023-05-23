<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router';
import { onMounted, ref } from 'vue';

import useChatsStore from '@/stores/chats';
import useMessagesStore from '@/stores/messages';
import { useAuthStore } from '@/stores/auth';
import useBreakpoints from '@/hooks/useBreakpoints';

import ChatList from '@/components/Chat/ChatList.vue';
import NavigationList from '@/components/ui/NavigationList.vue';
import IconAdd from '@/assets/icons/svg/icon-add.svg?component';
import Burger from '@/assets/icons/svg/menu.svg?component';
import Close from '@/assets/icons/svg/modal-close.svg?component';
import SideBarButton from './SideBarButton.vue';

const chats = useChatsStore();
const messages = useMessagesStore();
const auth = useAuthStore();
const { isMobile } = useBreakpoints();
const router = useRouter();
const route = useRoute();

const showSidebar = route.name === 'home' && auth.activateAnimation ? ref(false) : ref(true);
const isOpen = ref(false);

const newChat = () => {
  chats.clearActiveChat();
  messages.messages = [];
  isOpen.value = false;
  router.push('/');
};

onMounted(() => {
  if (!chats.chats || chats.chats.length === 0) {
    chats.getChats();
  }
  setTimeout(() => {
    showSidebar.value = true;
  }, 900);
});
</script>

<template>
  <div
    class="dark bg-opacity-50 bg-black"
    id="sidebar"
    :class="[!showSidebar ? 'hide-sidebar' : '', isMobile ? 'w-full' : '', isOpen ? 'overflow-y-auto' : 'overflow-hidden']"
    :style="{
      'background-color': isMobile ? '#261651' : '',
    }">
    <div class="flex flex-col space-y-1" :class="[isMobile ? '' : 'h-full p-2']">
      <SideBarButton
        v-if="!isMobile"
        @clicked="newChat"
        description="New chat"
        :has-border="true"
      >
        <template #icon>
          <IconAdd class="w-5 h-5 fill-gray-200" />
        </template>
      </SideBarButton>
      <div v-else class="new-chat flex items-center justify-between">
        <Burger v-if="!isOpen" @click="isOpen = true" />
        <Close v-else @click="isOpen = false" :style="{ width: '22px' }" />
        <span v-if="route.name !== 'home'">New chat</span>
        <IconAdd v-if="route.name !== 'home'" class="w-5 h-5 fill-gray-200" @click="newChat" />
      </div>
      <div v-if="isMobile" class="sidebar__content grow flex flex-col justify-between" :class="[isMobile && isOpen ? 'h-screen' : 'h-0']">
        <ChatList class="grow" />
        <NavigationList class="flex-none" />
      </div>
      <div v-if="!isMobile" class="grow flex flex-col justify-between">
        <ChatList class="grow" />
        <NavigationList class="flex-none" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

#sidebar {
  transition: all 0.4s ease;
  top: 0;
  bottom: 0;

  @media screen and (max-width:600px) {
    top: unset;
    bottom: unset;
  }
  .new-chat {
    padding: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);

    span {
      @include Inter(16px, 18px);
      color: $white;
    }
  }

  .sidebar__content {
    transition: all 0.5s ease;
    margin: 0;
  }
}

.hide-sidebar {
  width: 0;
}

</style>
