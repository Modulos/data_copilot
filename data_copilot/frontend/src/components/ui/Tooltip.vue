<!-- eslint-disable vue/multi-word-component-names -->
<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

defineProps({
  text: {
    type: String,
    required: true,
  },
});

const x = ref(0);
const y = ref(0);

const updatePosition = (event: MouseEvent) => {
  x.value = event.clientX - 15;
  y.value = event.clientY;
};

onMounted(() => {
  document.addEventListener('mousemove', updatePosition);
});

onBeforeUnmount(() => {
  document.removeEventListener('mousemove', updatePosition);
});
</script>
<template>
  <div class="tooltip" :style="{ top: y + 'px', left: x + 'px' }">
    <span class="tooltip__text"> {{ text }}</span>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.tooltip {
  position: fixed;
  top: 0;
  left: 0;
  padding: 6px 12px;
  background: $white;
  border-radius: 8px;
  pointer-events: none; /* make sure the element doesn't interfere with mouse events */
  z-index: 9999; /* set a high z-index to ensure the element is always on top */
  transform: translate(0, -110%);
  &__text {
    @include Inter(14px, 18px);
    font-weight: 400;
    color: $dark-blue
  }
}
.tooltip::before {
  content: '';
  position: absolute;
  bottom: -7px;
  left: 10px;
  width: 0;
  height: 0;
  border-left: 6px solid transparent;
  border-right: 7px solid transparent;
  border-top: 8px solid $white;
}
</style>
