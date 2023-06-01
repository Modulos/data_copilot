<script setup lang="ts">
import { useRouter } from 'vue-router';
import useArtifactStore from '@/stores/artifacts';
import useChatsStore from '@/stores/chats';

import UploadDataset from '@/assets/icons/svg/upload-dataset.svg?component';
import Loader from '@/components/ui/Loader.vue';

const artifactStore = useArtifactStore();
const chatStore = useChatsStore();
const router = useRouter();

const upload = async (event: any) => {
  const file = event.target.files[0];

  await artifactStore.createArtifact(file.name);
  const response = await artifactStore.uploadArtifact(file);

  if (!response) {
    return;
  }

  await chatStore.createChat(artifactStore.artifact_id, file.name);
  if (chatStore.activeChat) {
    await chatStore.getActiveDatasetNameAndArtifactVersion();
    router.push(`/chat-welcome/${chatStore.activeChat}`);
  }
};
</script>

<template>
  <div class="dropzone__wrapp flex items-center justify-center w-full border-2 border-gray-300 border-dashed rounded-lg">
    <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-32 cursor-pointer">
      <div class="flex flex-col items-center justify-center">
        <UploadDataset v-if="!artifactStore.isLoading" class="mb-3" />
        <Loader class="mb-3" v-else />
        <p class="mb-2 text-white">
          Click to upload your dataset or drag and drop
        </p>
        <p class="white">.csv|.xls|.xlsx</p>
      </div>
      <input id="dropzone-file" type="file" class="hidden" @change="upload" :disabled="artifactStore.isLoading" />
    </label>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.dropzone__wrapp {
  background: rgba(37, 32, 98, 0.3);
  @include Inter(14px, 18px);
  font-weight: 400;
  padding: 10px;

  p {
    max-width: 250px;
    text-align: center;
  }

  p:last-child {
    opacity: 0.6;
  }
}
</style>
