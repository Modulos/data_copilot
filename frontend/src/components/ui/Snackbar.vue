<!-- eslint-disable vue/multi-word-component-names -->
<script lang="ts" setup>
import useArtifactStore from '@/stores/artifacts';
import { shallowRef, ref, watch } from 'vue';

import SuccessIcon from '@/assets/icons/svg/success.svg';
import AlertIcon from '@/assets/icons/svg/alert.svg';

const artifactStore = useArtifactStore();

interface IconMap {
  [key: string]: string;
}

defineProps({
  type: {
    type: String,
    default: 'success',
  },
  text: {
    type: String,
    default: '',
  },
});

const icons = shallowRef<IconMap>({
  success: SuccessIcon,
  alert: AlertIcon,
});

const hide = ref(true);

watch(
  () => artifactStore.showSnackbar,
  (newValue) => {
    if (newValue) {
      hide.value = false;
      setTimeout(() => {
        hide.value = true;
      }, 3500);
    }
  },
);
</script>

<template>
  <div v-if="!hide" class="snackbar flex">
    <component :is="icons[type]" />
    <span>{{ text }}</span>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.snackbar {
  position: absolute;
  bottom: 25px;
  right: 50px;
  z-index: 99;
  padding: 17px 14px;
  background: linear-gradient(
      0deg,
      rgba(255, 255, 255, 0.9),
      rgba(255, 255, 255, 0.9)
    ),
    #4caf50;
  border-radius: 4px;
  filter: drop-shadow(0px 4px 4px rgba(0, 0, 0, 0.25));
  span {
    @include Inter(14px, 18px);
    font-weight: 400;
    color: #313033;
    margin-left: 14px;
  }
}
</style>
