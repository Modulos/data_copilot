<script setup lang="ts">
import { ref, watch } from 'vue';
import useChatsStore from '@/stores/chats';
import useModalStore from '@/stores/modal';

import EditBtn from '@/assets/icons/svg/dataset-edit.svg?component';
import DeleteBtn from '@/assets/icons/svg/dataset-delete.svg?component';
import SaveBtn from '@/assets/icons/svg/dataset-save.svg?component';
import ClearBtn from '@/assets/icons/svg/dataset-clear.svg?component';

import Tooltip from '@/components/ui/Tooltip.vue';

const props = defineProps({
  id: {
    type: String,
    default: '',
  },
  description: { type: String, required: true },
  hasBorder: Boolean,
  active: Boolean,
  hasActions: Boolean,
  canBeInput: Boolean,
});

const chatStore = useChatsStore();
const modalStore = useModalStore();
const editActive = ref(false);
const showTooltip = ref(false);
const editInput = props.description ? ref(props.description) : ref('');

async function deleteChat() {
  modalStore.fillModal('Delete chat', 'Would you like to permanently delete this chat?');
  modalStore.openModal(chatStore.deleteChat, props.id);
}

function editChat() {
  editActive.value = true;
}

async function saveChat() {
  modalStore.fillModal('Change chat name', 'Would you like to change chat name?');
  if (editInput.value !== '') {
    modalStore.openModal(chatStore.editChat, props.id, editInput.value);
  }
}

function clearInput() {
  editInput.value = '';
}

watch(() => modalStore.isActive, (newValue) => {
  if (!newValue) {
    editActive.value = false;
  }
});
</script>

<template>
  <div
    @click="$emit('clicked')"
    :class="[
      hasBorder ? ['border', 'border-gray-200'] : '',
      active ? 'bg-blue-600' : '',
      hasActions ? 'justify-between' : '',
    ]"
    class="container p-4 mt-3 flex items-center rounded-md duration-300 cursor-pointer hover:bg-blue-600 text-white"
  >
    <div class="flex items-center">
      <slot name="icon" />
      <div class="chat__name" v-if="!editActive">
        <span
          @mouseover="showTooltip = true"
          @focus="showTooltip = true"
          @mouseleave="showTooltip = false"
          @blur="showTooltip = false">
          {{ description }}
        </span>
        <Tooltip v-if="showTooltip && hasActions" :text="description" />
      </div>
      <input v-if="editActive && canBeInput" type="text" name="edit" v-model="editInput" @click.stop @input.stop @change.stop>
      <label for="edit" />
    </div>
    <div v-if="hasActions" class="actions__container flex">
      <EditBtn v-if="!editActive" @click.stop="editChat" />
      <SaveBtn v-else @click.stop="saveChat" />
      <DeleteBtn v-if="!editActive" @click.stop="deleteChat" />
      <ClearBtn v-else @click.stop="clearInput" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";
.container {
  position: relative;
  .chat__name {
    position: relative;
    span {
      @include Inter(14px, 18px);
      font-weight: 400;
      margin-left: 20px;
      display: inline-block;
      overflow: hidden;
      max-width: 130px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      @media screen and (max-width:600px) {
        max-width: unset;
      }
      @media screen and (max-width:425px) {
        max-width: 190px;
      }
    }
  }

  input {
    max-width: 130px;
    background: transparent;
    border-bottom: 1px solid $white;
    outline: none;
  }
  .actions__container {
    svg:not(:last-child) {
      margin-right: 10px;
    }
    svg:hover {
      opacity: 0.5;
    }
  }
}

</style>
