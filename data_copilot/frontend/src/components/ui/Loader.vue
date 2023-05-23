<!-- eslint-disable vue/multi-word-component-names -->
<script lang="ts" setup></script>

<template>
  <div class="loader">
    <div class="circle" />
  </div>
</template>

<style lang="scss" scoped>
.loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.circle {
  width: 27px;
  height: 27px;
  border: 2px solid #27FFC6;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
