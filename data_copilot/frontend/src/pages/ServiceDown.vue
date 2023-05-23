<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import Logo from '@/assets/icons/svg/logo-landing.svg?component';
import ModulosFooter from '@/components/ModulosFooter.vue';
</script>

<template>
  <div class="page__wrapp flex flex-col justify-center">
    <div class="logo__container w-full flex justify-center">
      <router-link to="/" class="contents">
        <Logo class="logo" />
      </router-link>
    </div>
    <div class="content__container flex flex-col items-center">
      <h2>Service is down.</h2>
      <p>
        Service is unstable at the moment, wait some minutes or contact us
        by e-mail.
      </p>
    </div>
    <ModulosFooter class="w-full absolute bottom-5 !max-w-none" />
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";
.page__wrapp {
  min-height: 100vh;
  .logo__container {
    position: absolute;
    top: 6%;
    .logo {
      transform: scale(0.58);
    }
  }
  .content__container {
    h2 {
      @include Inter(52px , 63px);
      font-weight: 700;
      margin-top: 25px;
      margin-bottom: 40px;
    }
    p {
      font-weight: 400;
      @include Inter(16px, 24px);
    a {
      text-decoration: none;
      font-weight: 600;
      }
    }
  }

}
</style>
