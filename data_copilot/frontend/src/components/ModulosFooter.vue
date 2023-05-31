<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import useBreakpoints from '@/hooks/useBreakpoints';

import IconModulos from '@/components/icons/IconModulos.vue';
import NavigationList from '@/components/ui/NavigationList.vue';

const route = useRoute();
const auth = useAuthStore();
const { isMobile } = useBreakpoints();

const isLogin = computed(() => route.name === 'login' || route.name === 'not-found' || route.name === 'service-down' || route.name === 'signup');
const isError = computed(() => route.name === 'not-found' || route.name === 'service-down');

const showFooter = route.name === 'home' && auth.activateAnimation ? ref(false) : ref(true);

onMounted(() => {
  setTimeout(() => {
    showFooter.value = true;
  }, 750);
});
</script>
<template>
  <div v-if="showFooter" class="footer__wrapp flex justify-center text-white text-xs" :class="[route.name !== 'chat/:id' ? 'spec-position' : '']">
    <div>
      <div v-if="isLogin" class="flex items-center justify-center mb-4">
        <IconModulos />
      </div>
      <NavigationList v-if="route.name === 'service-down'" class="flex-none mb-5" :only-social="true" />
      <p class="text-center opacity-50" :class="[isMobile ? 'mb-0' : 'mb-4']">
        © 2023 Modulos AG. All Rights Reserved
      </p>
      <p v-if="!isError" class="px-6 text-center opacity-50 hidden md:block">
        Modulos Data Copilot beta.
      </p>
      <p v-if="!isError" class="text-center opacity-50 block md:hidden" :class="isMobile ? 'px-0' : 'px-6'">
        Modulos Data Copilot beta.
        <span class="underline">Read more</span>
      </p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.footer__wrapp {
  max-width: 70%;
  @media screen and (max-width:600px) {
    max-width: 100%;
  }
  p {
    @include Inter(12px, 18px);
    font-weight: 400;
    span {
      opacity: 0.5;
    }
    .white {
      opacity: 1;
    }
  }
}

.spec-position {
  position: absolute;
  bottom: 20px;
}
</style>
