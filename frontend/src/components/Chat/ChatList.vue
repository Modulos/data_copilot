<script setup lang="ts">
import useChatsStore from '@/stores/chats';
import ChatListItem from './ChatListItem.vue';

const chats = useChatsStore();

</script>

<template>
  <div
    class="chat-item__container flex-col flex-1 overflow-y-auto border-b border-white/20"
  >
    <ChatListItem
      v-for="chat in chats.chats"
      :key="chat.id"
      :title="chat.name"
      :chatId="chat.id"
    />
  </div>
</template>

<style lang="scss" scoped>
.chat-item__container{
  min-height: 300px;
}
.chat-item__container::-webkit-scrollbar {
  display: none;
}
</style>
