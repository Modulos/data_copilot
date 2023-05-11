<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<script setup lang="ts">
import * as d3 from 'd3';
import { onMounted } from 'vue';
import * as displayUtils from '@/components/databits_display/displayUtils';
import * as displayBarChart from '@/components/databits_display/displayBarChart';

const SomeID = displayUtils.getRandomId();

interface Margin {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

const margin = {
  top: 20, right: 20, bottom: 40, left: 40,
};
const width = 350 - margin.left - margin.right;
const height = 350 - margin.top - margin.bottom;

// const inputData = {
//     'data': {
//         'Female': 0.5445544554455446,
//         'Male': 0.45544554455445546
//     },
//     'others': 0
// }

const props = defineProps<{
  inputData: any;
}>();

function transformData(inputData: any) {
  const transformedData = { data: {}, others: 0 };
  const { categories, values } = inputData;
  for (let i = 0; i < categories.length; i += 1) {
    // @ts-ignore
    transformedData.data[categories[i]] = values[i];
  }
  return transformedData;
}

function drawBarChart(
  inputData: any,
  plotMargin: Margin,
  plotWidth: number,
  plotHeight: number,
  specialPoint = null,
) {
  const dataBinValuePairs = displayBarChart.transformToLabelValuePairs(
    inputData,
  );

  // Define x and y scales
  const x = d3
    .scaleLinear()
    .domain([0, d3.max(dataBinValuePairs, (d: displayBarChart.BarChartOutput) => d.value) as number])
    .range([0, plotWidth - plotMargin.right - plotMargin.left]);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(dataBinValuePairs, (d: displayBarChart.BarChartOutput) => d.value) as number])
    .range([plotHeight - plotMargin.bottom, plotMargin.top]);

  // Define x and y axes
  const xAxis = d3.axisBottom(x).ticks(5);
  const yAxis = d3.axisLeft(y).ticks(0);

  const plotGroup = displayUtils.addEmptySvgToContainer(SomeID);
  plotGroup.append('rect')
    .attr('x', plotMargin.left)
    .attr('y', plotMargin.top)
    .attr('width', plotWidth - plotMargin.left - plotMargin.right)
    .attr('height', plotHeight - plotMargin.top - plotMargin.bottom)
    .attr('fill', 'none')
    .attr('stroke', 'black')
    .attr('stroke-opacity', 0.1);

  plotGroup
    .append('g')
    .attr('transform', `translate(${plotMargin.left}, 0)`)
    .attr('class', 'axis')
    .call(yAxis);

  plotGroup
    .append('g')
    .attr('transform', `translate(${plotMargin.left}, ${plotHeight - plotMargin.bottom})`)
    .attr('class', 'axis')
    .call(xAxis);

  const bars = plotGroup.selectAll('.bar').data(dataBinValuePairs);

  const enterGroup = bars
    .enter()
    .append('g')
    .attr('class', 'bar')
    .attr(
      'transform',
      (d: any, i: number) => `translate(${plotMargin.left}, ${plotHeight - plotMargin.bottom - i * 40 - 40})`,
    );

  enterGroup
    .append('rect')
    .attr('x', 0)
    .attr('y', 12)
    .attr('width', (d: displayBarChart.BarChartOutput) => {
      // In case value is too small display at least 2.
      let retval = x(d.value);
      if (retval > 0 && retval < 2) {
        retval = 2;
      }
      return retval;
    })
    .attr('height', 10)
    .style('shape-rendering', 'crispEdges')
    .attr('fill', '#1C9ED6')
    .attr('stroke', 'none');

  enterGroup
    .append('text')
    .attr('x', 0)
    .attr('y', 0)
    .attr('dx', 4)
    .attr('dy', -4)
    .attr('class', 'barLabel')
    .attr('dominant-baseline', 'hanging')
    .text((d: displayBarChart.BarChartOutput) => `${d.label} (${d3.format('.2%')(d.value)})`);
}

onMounted(() => {
  drawBarChart(transformData(props.inputData.data), margin, width, height, null);
});

</script>
<template>
  <div class="flex flex-col bg-white rounded-md p-3 max-w-fit">
    <div>
      <h1 class="text-md text-gray-700 font-bold mb-3">{{ props.inputData.name }}</h1>
    </div>

    <div>

      <div :id=SomeID />
    </div>
  </div>

</template>

<style scoped></style>
