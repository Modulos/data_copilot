<!-- eslint-disable no-unused-vars -->
<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<script setup lang="ts">
import * as d3 from 'd3';
import { onMounted } from 'vue';
import * as displayUtils from '@/components/databits_display/displayUtils';
import * as displayHistogram from '@/components/databits_display/displayHistogram';

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

const props = defineProps<{
  inputData: any;
}>();

function drawHistogram(
  inputData: displayHistogram.HistogramInput,
  plotMargin: Margin,
  plotWidth: number,
  plotHeight: number,
  specialPoint = null,
) {
  const dataBinValuePairs = displayHistogram.transformToBinValuePairs(
    inputData,
  );

  // Define x and y scales
  const x = d3
    .scaleLinear()
    .domain(<[number, number]>d3.extent(dataBinValuePairs, (d) => d[0]))
    .range([plotMargin.left, plotWidth - plotMargin.right]);
  const y = d3
    .scaleLinear()
    .domain([0, <number>d3.max(dataBinValuePairs, (d) => d[1]) * 1.2])
    .range([plotHeight - plotMargin.bottom, plotMargin.top]);

  // Define x and y axes
  const xAxis = d3.axisBottom(x).ticks(5);
  const yAxis = d3.axisLeft(y).ticks(5).tickFormat(d3.format('.0%'));

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
    .attr('transform', `translate(0, ${plotHeight - plotMargin.bottom})`)
    .style('color', '#525252')
    .style('font-size', '12px')
    .call(xAxis);

  plotGroup
    .append('g')
    .attr('transform', `translate(${plotMargin.left}, 0)`)
    .style('color', '#525252')
    .style('font-size', '12px')
    .call(yAxis);

  const line = d3
    .line<number[]>()
    .x((d) => x(d[0]))
    .y((d) => y(d[1]))
    .curve(d3.curveStep);

  const area = d3
    .area<number[]>()
    .x((d) => x(d[0]))
    .y0(y(0))
    .y1((d) => y(d[1]))
    .curve(d3.curveStep);

  plotGroup
    .append('path')
    .datum(dataBinValuePairs)
    .style('fill', 'url(#linear-gradient)')
    .attr('opacity', 0.5)
    .attr('d', area);

  plotGroup
    .append('path')
    .datum(dataBinValuePairs)
    .attr('d', line)
    .style('fill', 'none')
    .style('stroke', '#1c9ed6')
    .style('stroke-width', '1.5px');

  const circle = plotGroup
    .append('circle')
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', 4)
    .attr('fill', 'none');

  const verticalLine = plotGroup
    .append('line')
    .attr('stroke', '#FF6224')
    .attr('opacity', 0)
    .attr('stroke-dasharray', '5,5');

  const horizontalLine = plotGroup
    .append('line')
    .attr('stroke', '#FF6224')
    .attr('opacity', 0)
    .attr('stroke-dasharray', '5,5');

  // add an invisible rectangle
  const overlay = plotGroup
    .append('rect')
    .attr('x', plotMargin.left)
    .attr('y', plotMargin.top)
    .attr('width', plotWidth - plotMargin.left - plotMargin.right)
    .attr('height', plotHeight - plotMargin.top - plotMargin.bottom)
    .attr('fill', 'red')
    .attr('opacity', 0);

  overlay
    .on('mousemove', (event) => {
      const [mx, my] = d3.pointer(event);
      const xValue = x.invert(mx);
      const index = d3.bisectLeft(dataBinValuePairs.map((d) => d[0]), xValue);
      const value = dataBinValuePairs[index];

      verticalLine
        .attr('x1', x(value[0]))
        .attr('x2', x(value[0]))
        .attr('y1', y(value[1]))
        .attr('y2', plotHeight - plotMargin.bottom)
        .attr('opacity', 1);

      horizontalLine
        .attr('x1', plotMargin.left)
        .attr('x2', x(value[0]))
        .attr('y1', y(value[1]))
        .attr('y2', y(value[1]))
        .attr('opacity', 1);

      circle
        .attr('cx', x(value[0]))
        .attr('cy', y(value[1]))
        .attr('fill', '#FF6224')
        .raise();

      overlay.raise();
    })
    .on('mouseout', () => {
      circle.attr('fill', 'none').attr('stroke', 'none');
      verticalLine.attr('opacity', 0);
      horizontalLine.attr('opacity', 0);
    });
}

onMounted(() => {
  drawHistogram(props.inputData.data, margin, width, height, null);
});

</script>
<template>
  <div class="flex flex-col bg-white rounded-md p-3 max-w-fit">
    <div>
      <h1 class="text-md text-gray-700 font-bold mb-3">Correlation Matrix</h1>
    </div>

    <div>

      <div :id=SomeID />
    </div>
  </div>
</template>

<style scoped></style>
