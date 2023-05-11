<script setup lang="ts">

const props = defineProps({
  description: { type: String, required: true },
});

</script>

<template>
  <div
    @click="$emit('clicked')"
    :class="[!!$slots.icon ? ['bg-white'] : ['bg-[#27FFC6]', 'justify-center']]"
    class="p-2.5 flex items-center rounded-sm px-4 duration-300 cursor-pointer text-white"

  >
    <slot name="icon" />
    <span
      class="text-[16px] text-black font-normal"
      :class="{ 'ml-4': !!$slots.icon }">{{
        props.description
      }}</span>
  </div>
</template>
