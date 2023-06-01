<script setup lang="ts">
import { computed } from 'vue';
import { getRandomId } from '@/components/databits_display/displayUtils';

const SomeID = getRandomId();
const props = defineProps<{
  inputData: any;
}>();

const header = computed(() => Object.keys(props.inputData.data));
const maxRows = computed(() => {
  let maximum = 0;
  const keys = Object.keys(props.inputData.data);
  for (let i = 0; i < keys.length; i += 1) {
    maximum = Math.max(maximum, props.inputData.data[keys[i]].length);
  }
  return maximum;
});

function formatValue(value: string) {
  if (value === undefined) {
    return '-';
  }

  return value;
}

</script>
<template>
  <div :id=SomeID>
    <div class="relative max-w-3xl overflow-x-auto shadow-md sm:rounded-lg">
      <table class="w-full text-left text-gray-500">
        <thead class=" text-gray-700 uppercase bg-gray-50">
          <tr>
            <th v-for="h in header" class="px-6 py-1" :key="h">{{ h }}</th>
          </tr>
        </thead>
        <tr v-for="r in maxRows" :key="r" class="bg-white border-b hover:bg-gray-100 ">
          <td v-for="h in header" class="px-6 py-1" :key="h">{{ formatValue(inputData.data[h][r - 1]) }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>
