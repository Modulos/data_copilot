<script setup lang="ts">
import SideBar from '@/components/SideBar/SideBar.vue';
</script>

<template>
  <SideBar
    class="fixed md:flex md:w-[260px] md:flex-col z-50"
  />
  <main class="relative z-40">
    <div class="overflow-hidden w-full h-full relative">
      <slot />
    </div>
  </main>
</template>

<style lang="scss" scoped>
main {
  padding-left: 260px;
  @media screen and (max-width:600px) {
    max-width: 320px;
    padding-left: 0;
    margin: 0 auto;
  }
}
</style>
