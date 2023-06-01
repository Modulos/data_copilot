<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import { ref, watch } from 'vue';
// eslint-disable-next-line import/no-cycle
import { useAuthStore } from '@/stores/auth';
import useBreakpoints from '@/hooks/useBreakpoints';
import { useRouter } from 'vue-router';

import InputField from '@/components/ui/InputField.vue';
import MainButton from '@/components/ui/MainButton.vue';
import Logo from '@/assets/icons/svg/logo-landing.svg?component';

const { isMobile } = useBreakpoints();
const router = useRouter();

const email = ref<string | null>(null);
const faultyEmail = ref<boolean>(false);
const faultyLogin = ref<boolean>(false);
const password = ref<string | null>(null);
const askPassword = ref<boolean>(false);
const passwordRef = ref<(typeof InputField) | null>(null);

const onContinue = () => {
  // Check email string is a valid email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (email.value === null) {
    faultyEmail.value = true;
    return;
  }
  const validEmail = emailRegex.test(email.value);
  if (!validEmail) {
    faultyEmail.value = true;
    return;
  }
  // If valid, ask for password
  faultyEmail.value = false;
  askPassword.value = true;
};

const onContinueSubmit = () => {
  const authStore = useAuthStore();
  // Check password string is a valid password
  if (password.value === null || email.value === null) {
    return;
  }
  authStore.login(email.value, password.value).catch((error) => {
    faultyLogin.value = true;
    console.log(error);
  });
};

watch(passwordRef, () => {
  if (passwordRef.value) {
    passwordRef.value.focusOnElement();
  }
});
</script>

<template>
  <div class="login__wrapp flex flex-col justify-center relative z-40" :class="[isMobile ? 'mb-32' : 'mb-28']">
    <div class="w-full flex justify-center pt-[13%] xl:pt-[5%] 2xl:pt-[2%]">
      <Logo class="logo" />
    </div>
    <div class="grow">
      <div class="w-full flex justify-center mt-16 md:mt-24">
        <h1 class="text-center text-6xl font-bold text-white">
          Welcome
        </h1>
      </div>
      <div class="w-full flex justify-center mt-10 md:mt-14">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <InputField
            v-model="email"
            placeholder="E-mail Address"
            input-type="text"
            @keyup.enter="onContinue"
          />
          <p v-if="faultyEmail" class="mt-2 text-xs text-red-300">
            Not a valid Email Address
          </p>
        </div>
      </div>
      <div v-if="askPassword" class="w-full flex justify-center mt-10 md:mt-4">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <InputField
            ref="passwordRef"
            v-model="password"
            placeholder="Password"
            input-type="password"
            @keyup.enter="onContinueSubmit"
          />
          <p v-if="faultyLogin" class="mt-2 text-xs text-red-300">
            Looks like either the E-mail or the Password is wrong.
          </p>
        </div>
      </div>
      <div v-if="askPassword" class="w-full flex justify-center mt-4">
        <p class="opacity-50 text-white mr-1">Forgot Password?</p>
      </div>

      <div class="w-full flex justify-center mt-4">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <MainButton
            v-if="!askPassword"
            description="Continue"
            @clicked="onContinue"
          />
          <MainButton
            v-if="askPassword"
            description="Continue"
            @clicked="onContinueSubmit"
          />
        </div>
      </div>
      <div class="w-full flex justify-center mt-4">
        <p class="opacity-50 text-white mr-1">Don't have an account?</p>

        <span class="hover:opacity-60 hover:cursor-pointer text-[#27FFC6]" @click="router.push('/signup')"> Sign up </span>
      </div>
      <div v-if="!askPassword" class="w-full flex justify-center my-6" />
      <div
        v-if="!askPassword"
        class="w-full flex justify-center items-center flex-col md:flex-row"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login__wrapp  {
  @media screen and (max-width:600px) {
    max-width: 320px;
    margin: 0 auto 128px;
  }
}
h1 {
  @media screen and (max-width:600px) {
    font-size: 52px;
    line-height: 63px;
  }
}
.logo {
  transform: scale(0.6);

  @media screen and (max-width:600px) {
    transform: scale(0.58);
    overflow: unset;
  }
}

.social-button {
  @media screen and (max-width:600px) {
    width: 300px;
  }
}
</style>
