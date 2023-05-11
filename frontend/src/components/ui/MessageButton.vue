<script lang="ts" setup>
const props = defineProps({
  text: {
    type: String,
    required: true,
  },
});

const emit = defineEmits(['inputMessage']);

function inputMessage() {
  emit('inputMessage', props.text);
}
</script>

<template>
  <div class="message__wrapp" @click="inputMessage">
    <p class="message__text">{{ text }}</p>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.message__wrapp {
  max-width: 32%;
  padding: 14px 25px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  cursor: pointer;
  @media screen and (max-width:600px) {
    max-width: 100%;
    margin-bottom: 14px;
  }
  p {
    @include Inter(16px, 18px);
    font-weight: 400;
    text-align: center;
  }
}

.message__wrapp:hover {
  background: $greenishCyan;
  p {
    color: $dark-blue;
  }
}
</style>
