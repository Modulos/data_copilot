<script setup lang="ts">
import { onMounted, defineAsyncComponent, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import useModalStore from '@/stores/modal';
import { useRoute } from 'vue-router';

import Snackbar from '@/components/ui/Snackbar.vue';
import MainModal from '@/components/ui/MainModal.vue';

const authStore = useAuthStore();
const modalStore = useModalStore();
const route = useRoute();

const layoutComponent = computed(() => {
  const layoutName = route.meta.layout ?? 'Default';

  return defineAsyncComponent(
    () => import(`@/layouts/${layoutName}Layout.vue`),
  );
});

onMounted(() => authStore.startTimer());
</script>

<template>
  <div
    class="wrapp"
    :class="[route.name === 'chat/:id' ? 'message' : '', route.name === 'login' ? 'pb-4' : '']"
  >
    <component :is="layoutComponent">
      <RouterView />
    </component>
    <MainModal v-if="modalStore.isActive" />
    <Snackbar type="success" text=" Successfully uploaded" />
    <img v-if="route.name !== 'chat/:id'" src="@/assets/images/waves.webp" alt="waves">
  </div>
</template>

<style lang="scss" scoped>
.wrapp {
  background-image: url("@/assets/images/data-copilot-bg.webp");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  min-height: 100vh;

  img {
    width: 98%;
    position: fixed;
    bottom: 0;
    z-index: 1;
  }
}
</style>
