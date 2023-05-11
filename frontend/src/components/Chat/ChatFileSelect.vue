<script setup lang="ts">
import SelectDataset from '@/assets/icons/svg/select-dataset.svg?component';
</script>

<template>
  <div
    class="select__wrapp flex items-center justify-center w-full border-2 border-gray-300 rounded-lg"
  >
    <div
      class="flex flex-col items-center justify-center w-full h-32 cursor-pointer"
    >
      <div class="flex flex-col items-center justify-center pt-5 pb-6">
        <SelectDataset class="mb-4" />
        <p class="mb-2">Click to select a dataset from the list</p>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.select__wrapp {
  background: rgba(37, 32, 98, 0.3);
  @include Inter(14px, 18px);
  font-weight: 400;
  padding: 10px;
  p {
    max-width: 190px;
    text-align: center;
  }
}
</style>
