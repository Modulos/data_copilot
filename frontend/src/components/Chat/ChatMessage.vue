<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import type { Message } from '@/client/api';
import useBreakpoints from '@/hooks/useBreakpoints';

import IconModulosLogo from '@/components/icons/IconModulosLogo.vue';
import CorrelationMatrix from '@/components/databits_display/CorrelationMatrixPlot.vue';
import HistogramPlot from '@/components/databits_display/HistogramPlot.vue';
import TableDisplay from '@/components/databits_display/TableDisplay.vue';
import BarChartPlot from '@/components/databits_display/BarChartPlot.vue';

import getFirstLetters from '@/helpers/globalFunctions';

const root = ref<HTMLElement | null>(null);
const authStore = useAuthStore();
const { isMobile } = useBreakpoints();

defineExpose({
  scrollToElement() {
    if (root.value) {
      root.value.scrollIntoView();
    }
  },
});

const props = defineProps<{
  message: Message;
}>();

function getText(componentData: any) {
  return componentData.data.text;
}

</script>

<template>
  <div ref="root" class="w-full text-white" :style="{ 'background-color': props.message.system_generated ? 'rgba(255, 255, 255, 0.1' : '' }">
    <div
      class="flex  text-base gap-4 md:gap-6 m-auto md:max-w-2xl lg:max-w-2xl xl:max-w-3xl p-4 md:py-6 flex lg:px-0"
      :class="[isMobile ? 'flex-col' : 'flex-row']">
      <div>
        <IconModulosLogo v-if="props.message.system_generated" class="bg-white p-1 w-7 h-7 fill-black" />
        <div v-if="authStore.user && !props.message.system_generated" class="default__avatar flex items-center justify-center">
          {{ authStore.user.first_name ? getFirstLetters(authStore.user.first_name) : (getFirstLetters('Data') + (authStore.user.last_name ? getFirstLetters(authStore.user.last_name) : getFirstLetters('Copilot')))}}
        </div>
      </div>
      <div
        v-if="!props.message.system_generated || props.message.content_type === 'error' || props.message.content_type === 'text'">
        {{ props.message.content }}
      </div>
      <div class="response__content flex flex-col" v-else>
        <div :class="[isMobile ? 'mx-0 my-3' : 'm-3']" v-for="component in props.message.content?.components" :key="component.name || '' + component.description">
          <TableDisplay v-if="component.type === 'table'" :inputData="component" />
          <HistogramPlot v-else-if="component.type === 'plot_hist'" :inputData="component" />
          <BarChartPlot v-else-if="component.type === 'plot_bar'" :inputData="component" />
          <CorrelationMatrix v-else-if="component.type === 'plot_heatmap'" :inputData="component" />
          <div v-else-if="component.type === 'text'" v-html="getText(component)" />
          <div class="my-3" v-if="component.config?.show_description"> {{ component.description }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "@/assets/styles/main.scss";

.default__avatar {
  width: 30px;
  height: 30px;
  background: #9547D2;
  border-radius: 2px;
  @include Inter(14px, 24px);
  font-weight: 600;
  color: $white;

}
.response__content {
  :deep(svg) {
    max-width: 100%;
  }
}

</style>
