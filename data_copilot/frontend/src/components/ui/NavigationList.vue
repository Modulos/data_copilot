<script setup lang="ts">
import { useRouter } from 'vue-router';

import SideBarButton from '@/components/SideBar/SideBarButton.vue';
import IconDelete from '@/components/icons/IconDelete.vue';
import IconLogout from '@/components/icons/IconLogout.vue';
import IconLocalPolice from '@/components/icons/IconLocalPolice.vue';
import IconGavel from '@/components/icons/IconGavel.vue';
import useMessagesStore from '@/stores/messages';
import useChatsStore from '@/stores/chats';
import { useAuthStore } from '@/stores/auth';
import useModalStore from '@/stores/modal';
import IconYoutube from '../icons/IconYoutube.vue';
import IconLinkedin from '../icons/IconLinkedin.vue';
import IconTwitter from '../icons/IconTwitter.vue';

defineProps({
  onlySocial: {
    type: Boolean,
  },
});

const messages = useMessagesStore();
const chats = useChatsStore();
const auth = useAuthStore();
const router = useRouter();
const modalStore = useModalStore();

const clearChat = () => {
  // Clear all chat and messages from the store
  messages.clearMessages();
  chats.clearChats();
  router.push('/');
};

function routeToPage(url: string) {
  window.open(url, '_blank');
}

const logout = () => {
  auth.logout();
};

async function deleteAllChat() {
  modalStore.fillModal('Delete all chats', 'Would you like to permanently delete all chats?');
  modalStore.openModal(clearChat);
}

</script>

<template>
  <div class="flex-col">
    <div v-if="!onlySocial">
      <SideBarButton description="Clear Conversations" @clicked="deleteAllChat">
        <template #icon>
          <IconDelete class="w-5 h-5 fill-gray-200" />
        </template>
      </SideBarButton>
      <SideBarButton description="Privacy Policy" @clicked="() => routeToPage('https://www.modulos.ai/privacy-policy/')">
        <template #icon>
          <IconLocalPolice class="w-5 h-5 fill-gray-200" />
        </template>
      </SideBarButton>
      <SideBarButton description="Terms and Conditions" @clicked="() => routeToPage('https://www.modulos.ai/terms-and-conditions/')">
        <template #icon>
          <IconGavel class="w-5 h-5 fill-gray-200" />
        </template>
      </SideBarButton>
      <SideBarButton description="Logout" @clicked="logout">
        <template #icon>
          <IconLogout class="w-5 h-5 fill-gray-200" />
        </template>
      </SideBarButton>
    </div>
    <div class=" md:mt-6 mb-2 flex flex-row justify-center">
      <a class="mx-2" href="https://twitter.com/modulos_ai" target="_blank" rel="noopener noreferrer">
        <IconTwitter class="w-5 h-5 fill-gray-200" />
        <span>Twitter</span>
      </a>
      <a class="mx-2" href="https://ch.linkedin.com/company/modulos-ag" target="_blank" rel="noopener noreferrer">
        <IconLinkedin class="w-5 h-5 fill-gray-200" />
        <span>Linkedin</span>
      </a>
      <a class="mx-2" href="https://www.youtube.com/@modulos-ai" target="_blank" rel="noopener noreferrer">
        <IconYoutube class="w-5 h-5 fill-gray-200" />
        <span>Youtube</span>
      </a>
    </div>
  </div>
</template>

<style lang="scss" scoped>

a {
  span {
    position: absolute;
    left: -100%;
  }
}

</style>
