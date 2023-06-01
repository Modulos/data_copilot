<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { onClickOutside } from '@vueuse/core';
import useArtifactStore from '@/stores/artifacts';
import useChatsStore from '@/stores/chats';
import ModalClose from '@/assets/icons/svg/modal-close.svg?component';
import DatasetIcon from '@/assets/icons/svg/dataset-icon.svg?component';
import DatasetDelete from '@/assets/icons/svg/dataset-delete.svg?component';
// import DatasetEdit from '@/assets/icons/svg/dataset-edit.svg?component';
import DatasetSynced from '@/assets/icons/svg/dataset-synced.svg?component';

const router = useRouter();
const store = useChatsStore();
const artifactsStore = useArtifactStore();
const emit = defineEmits(['closeModal']);
const modal = ref(null);
onClickOutside(modal, () => emit('closeModal'));
function closeModal() {
  emit('closeModal');
}
// function getFormattedTimeDifference(creationDate: string) {
//   const now = new Date();
//   const diffInMs = now.getTime() - new Date(creationDate).getTime();
//   const diffInMinutes = Math.round(diffInMs / 60000);
//   const diffInHours = Math.round(diffInMs / 3600000);
//   const diffInDays = Math.round(diffInMs / 86400000);
//   if (diffInMinutes < 60) {
//     return `${diffInMinutes} minutes ago`;
//   } if (diffInHours < 24) {
//     return `${diffInHours} hours ago`;
//   }
//   return `${diffInDays} days ago`;
// }
const openChat = async (id: string, name: string) => {
  emit('closeModal');
  await store.createChat(id, name);
  if (store.activeChat) {
    await store.getActiveDatasetNameAndArtifactVersion();
    router.push(`/chat-welcome/${store.activeChat}`);
  }
};

const deleteArtifact = async (id: string) => {
  await artifactsStore.deleteArtifact(id);
};

</script>

<template>
  <div ref="modal" class="modal__wrapp flex flex-col">
    <div class="modal__top flex flex-col">
      <h2 class="modal__title">Select a dataset from the list</h2>
      <div class="datasets__container">
        <div
          v-for="dataset in artifactsStore.artifacts"
          :key="dataset.id"
          class="dataset flex justify-between items-center"

        >
          <div
            class=" dataset__left flex grow mr-2 hover:opacity-60"
            @click="openChat(dataset.id, dataset.name)">
            <DatasetIcon />
            <div class="dataset__info flex flex-col">
              <h3 class="dataset__name">{{ dataset.name }}</h3>
            </div>
          </div>
          <div class="dataset__right flex">
            <div class="dataset__icons flex">
              <DatasetDelete @click="deleteArtifact(dataset.id)" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="modal__footer flex">
      <DatasetSynced />
      <span>Last synced: 3 mins ago</span>
    </div>
    <ModalClose class="modal-close" @click="closeModal" />
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";
.modal__wrapp {
  width: 530px;
  max-height: 466px;
  position: relative;
  background: $navy;
  border-radius: 10px;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.4);
  overflow-y: scroll;
  z-index: 1;

  @media screen and (max-width:600px) {
    max-width: 320px;
  }
  .modal__top {
    padding: 30px 16px 30px 32px;
    margin-bottom: 20px;
    .modal__title {
      @include Inter(16px, 19px);
      font-weight: 700;
      margin-bottom: 40px;
    }
    .datasets__container {
      .dataset {
        cursor: pointer;
        padding: 0 14px 16px 0;
        .dataset__info {
          margin-left: 20px;
          .dataset__name {
            @include Inter(16px, 19px);
            margin-bottom: 5px;

            @media screen and (max-width:600px) {
              width: 125px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }
          }
          .dataset__time {
            @include Inter(14px, 19px);
            font-weight: 400;
          }
        }
        .dataset__size {
          @include Inter(11px, 12px);
          font-weight: 700;
          margin-right: 25px;
        }
        .dataset__icons {
          svg {
            cursor: pointer;
            opacity: 0.6;
          }
          svg:hover {
            opacity: 1;
          }
          .dataset-edit {
            margin-right: 10px;
          }
        }
      }
      .dataset:not(:last-child) {
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(235, 239, 242, 0.5);
      }
    }
  }
  .modal__footer {
    padding: 15px 20px;
    @include Inter(14px, 19px);
    font-weight: 400;
    border-top: 1px solid #3b3e66;
    span {
      margin-left: 8px;
    }
  }
  .modal-close {
    position: absolute;
    top: 19px;
    right: 19px;
    cursor: pointer;
  }
}
.modal__wrapp::-webkit-scrollbar {
  display: none;
}
</style>
