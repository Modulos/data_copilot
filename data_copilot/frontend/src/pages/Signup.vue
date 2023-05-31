<!-- eslint-disable vue/multi-word-component-names -->
<script setup lang="ts">
import { ref, watch } from 'vue';
// eslint-disable-next-line import/no-cycle
import { useAuthStore } from '@/stores/auth';
import useBreakpoints from '@/hooks/useBreakpoints';
import { useRouter } from 'vue-router';

import Logo from '@/assets/icons/svg/logo-landing.svg?component';

import InputField from '@/components/ui/InputField.vue';
import MainButton from '@/components/ui/MainButton.vue';

const { isMobile } = useBreakpoints();

const router = useRouter();

const email = ref<string | null>(null);
const faultyEmail = ref<boolean>(false);
const faultySignUp = ref<boolean>(false);
const password = ref<string | null>(null);
const firstName = ref<string | null>(null);
const lastName = ref<string | null>(null);
const passwordRef = ref<(typeof InputField) | null>(null);
const faultyDetail = ref<string | null>(null);

const onContinueSubmit = () => {
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

  const authStore = useAuthStore();

  if (password.value === null || email.value === null
    || firstName.value === null || lastName.value === null) {
    return;
  }
  authStore.signup(
    firstName.value,
    lastName.value,
    password.value,
    email.value,
  ).catch((error) => {
    console.log(error);
    faultySignUp.value = true;
    faultyDetail.value = error.response.data.detail;
  });
};

watch(passwordRef, () => {
  if (passwordRef.value) {
    passwordRef.value.focusOnElement();
  }
});

// function that routes to the signup page

</script>

<template>
  <div class="login__wrapp flex flex-col justify-center relative z-40" :class="[isMobile ? 'mb-32' : 'mb-28']">
    <div class="w-full flex justify-center pt-[13%] xl:pt-[5%] 2xl:pt-[2%]">
      <Logo class="logo" />
    </div>
    <div class="grow">
      <div class="w-full flex justify-center mt-16 md:mt-24">
        <h1 class="text-center text-6xl font-bold text-white">
          Create your account
        </h1>
      </div>
      <div class="w-full flex justify-center mt-10 md:mt-14">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <InputField v-model="firstName" placeholder="First Name" input-type="text" @keyup.enter="onContinueSubmit" />
        </div>
      </div>
      <div class="w-full flex justify-center mt-10 md:mt-4">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <InputField v-model="lastName" placeholder="Last Name" input-type="text" @keyup.enter="onContinueSubmit" />
        </div>
      </div>
      <div class="w-full flex justify-center mt-10 md:mt-4">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <InputField v-model="email" placeholder="E-mail Address" input-type="text" @keyup.enter="onContinueSubmit" />
          <p v-if="faultyEmail" class="mt-2 text-xs text-red-300">
            Not a valid Email Address
          </p>
        </div>
      </div>
      <div class="w-full flex justify-center mt-10 md:mt-4">
        <div class="flex flex-col" :class="[isMobile ? 'w-80' : 'w-72']">
          <div>
            <InputField
              ref="passwordRef"
              v-model="password"
              placeholder="Password"
              input-type="password"
              @keyup.enter="onContinueSubmit" />
          </div>
          <p v-if="faultySignUp" class="mt-2 text-xs text-red-300">
            Looks like the SignUp failed please try again. {{ faultyDetail }}
          </p>
        </div>
      </div>

      <div class="w-full flex justify-center mt-4">
        <div :class="[isMobile ? 'w-80' : 'w-72']">
          <MainButton description="Continue" @clicked="onContinueSubmit" />
        </div>
      </div>
      <div class="w-full flex justify-center mt-4">
        <p class="opacity-50 text-white mr-1">Already have an account?</p>
        <span class="hover:opacity-60 hover:cursor-pointer text-[#27FFC6]" @click="router.push('/login')"> Log in </span>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login__wrapp {
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
