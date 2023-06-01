<script setup lang="ts">
import { ref } from 'vue';
import useModalStore from '@/stores/modal';
import { onClickOutside } from '@vueuse/core';

const modal = ref(null);
const modalStore = useModalStore();

onClickOutside(modal, () => modalStore.closeModal());

function closeModal() {
  modalStore.closeModal();
}

</script>
<template>
  <div class="mask flex justify-center items-center">
    <div ref="modal" class="modal flex flex-col" :class="[modalStore.isActive ? 'visible' : '']">
      <h3 class="modal__title">{{ modalStore.title }}</h3>
      <p class="modal__description">{{ modalStore.description }}</p>
      <div class="modal__actions flex justify-between">
        <button class="cancel" type="button" @click="closeModal">Cancel</button>
        <button class="confirm" type="button" @click="modalStore.confirm()">Confirm</button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";
.mask {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  .modal {
    width: 330px;
    padding: 24px;
    background: $white;
    box-shadow: 0px 8px 36px rgba(0, 0, 0, 0.25);
    border-radius: 16px;
    opacity: 0;
    transition: all 0.5s ease;
    &__title {
      @include Inter(19px, 24px);
      font-weight: 700;
      color: $black;
    }
    &__description {
      @include Inter(14px, 20px);
      font-weight: 400;
      color: rgba(21, 25, 32, 0.5);
      margin: 24px 0;
    }
    &__actions {
      button {
        @include Inter(14px, 24px);
        padding: 10px 40px;
        font-weight: 600;
        border-radius: 8px;
      }
      .cancel {
        border: 1px solid rgba(86, 103, 137, 0.26);
        color: rgba(21, 25, 32, 0.5);
      }
      .confirm {
        background: #3772d6;
      }
    }
  }
  .visible {
    opacity: 1;
  }
}
</style>
