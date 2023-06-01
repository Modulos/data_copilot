<script setup lang="ts">
import { ref } from 'vue';

defineProps(['modelValue', 'placeholder', 'inputType']);
defineEmits(['update:modelValue']);

const root = ref<HTMLElement | null>(null);

defineExpose({
  focusOnElement() {
    if (root.value) {
      root.value.focus();
    }
  },
});
</script>

<template>
  <div class="relative h-14 w-full min-w-[200px]">
    <input
      ref="root"
      :id="'inputField' + modelValue"
      :type="inputType"
      :value="modelValue"
      @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
      class="peer h-full w-full rounded-[7px] border border-[#27FFC6] border-t-transparent bg-transparent px-3 py-2 outline outline-0 transition-all placeholder-shown:border placeholder-shown:border-[#27FFC6] placeholder-shown:border-t-[#27FFC6]  focus:border-2 focus:border-t-transparent text-white"
      placeholder=" " />
    <label
      :for="'inputField' + modelValue"
      class="before:content[' '] after:content[' ']
            pointer-events-none absolute left-0 -top-1.5 flex h-full w-full
            select-none font-normal leading-tight text-[#27FFC6] text-[11px]
            transition-all
            before:pointer-events-none before:mt-[6.5px]
            before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5
            before:rounded-tl-md before:border-t before:border-l
            before:border-[#27FFC6] before:transition-all
            after:pointer-events-none after:mt-[6.5px] after:ml-1
            after:box-border after:block after:h-1.5 after:w-2.5
            after:flex-grow after:rounded-tr-md after:border-t
            after:border-r after:border-blue-gray-200
            after:transition-all
            peer-placeholder-shown:leading-[4.25]
            peer-placeholder-shown:text-base
            peer-placeholder-shown:text-white
            peer-placeholder-shown:text-opacity-50
            peer-placeholder-shown:before:border-transparent
            peer-placeholder-shown:after:border-transparent
            peer-focus:text-[11px] peer-focus:leading-tight
            peer-focus:text-[#27FFC6] peer-focus:before:border-t-2
            peer-focus:before:border-l-2 peer-focus:before:border-[#27FFC6]
            peer-focus:after:border-t-2 peer-focus:after:border-r-2
            peer-focus:after:border-[#27FFC6]
            peer-disabled:text-transparent
            peer-disabled:before:border-transparent
            peer-disabled:after:border-transparent
            peer-disabled:peer-placeholder-shown:text-blue-gray-500">
      {{ placeholder }}
    </label>

  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

</style>
