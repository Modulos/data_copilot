<!-- eslint-disable @typescript-eslint/no-unused-vars -->
<!-- eslint-disable no-unused-vars -->
<script setup lang="ts">
import * as d3 from 'd3';
import { onMounted } from 'vue';
import type * as displayCorrelationMatrix from '@/components/databits_display/displayCorrelationMatrix';
import { getRandomId } from '@/components/databits_display/displayUtils';

const SomeID = getRandomId();

const truncate = (s: string) => s.replace(/(.{12})..+/, '$1…');

const props = defineProps<{
  inputData: any;
}>();

function transformData(inputData: any) {
  const transformedData = { values: {} };

  const { columns, rows, values } = inputData.data;

  for (let i = 0; i < columns.length; i += 1) {
    // @ts-ignore
    transformedData.values[columns[i]] = {};
    for (let j = 0; j < rows.length; j += 1) {
      // @ts-ignore
      transformedData.values[columns[i]][rows[j]] = values[i][j];
    }
  }
  return transformedData;
}

function drawCorrelationMatrix(
  inputData: displayCorrelationMatrix.CorrelationMatrixInput,
  specialPoint = null,
  cellSize: number = 50,
  addCircles: boolean = true,
  addRectangles: boolean = false,
  lowerOnly: boolean = false,
) {
  const featureNames = Object.keys(inputData.values);

  const width = cellSize * featureNames.length;
  const height = cellSize * featureNames.length;
  const scale = d3.scaleSqrt().domain([0, 1]).range([2, cellSize / 2 - 3]);
  const radius = (value: number) => scale(Math.abs(value));

  const colorInterpolator = d3.interpolateBrBG;
  const colorScale = d3.scaleSequential(colorInterpolator).domain([-1.8, 1.8]);

  // const warningSvg = '<svg width="22" height="19" viewBox="0 0 22 19" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M0 19L11 0L22 19H0ZM3.45 17H18.55L11 4L3.45 17ZM11 16C11.2833 16 11.521 15.904 11.713 15.712C11.9043 15.5207 12 15.2833 12 15C12 14.7167 11.9043 14.4793 11.713 14.288C11.521 14.096 11.2833 14 11 14C10.7167 14 10.4793 14.096 10.288 14.288C10.096 14.4793 10 14.7167 10 15C10 15.2833 10.096 15.5207 10.288 15.712C10.4793 15.904 10.7167 16 11 16ZM10 13H12V8H10V13Z" fill="#F59E0B"/></svg>';

  // Add elements to the DOM
  const parent = d3.select(`#${SomeID}`);
  parent.selectAll('*').remove();

  // Add warning
  // TODO add warning div

  // Find the longest feature name
  const longestFeatureName = featureNames.reduce((a, b) => (a.length > b.length ? a : b));
  const longestFeatureNameLength = longestFeatureName.length;
  const longestFeatureNameSpace = longestFeatureNameLength * 12;

  const container = parent.append('div');

  const margin = {
    top: 30, right: longestFeatureNameSpace / 3, bottom: longestFeatureNameSpace / 3, left: longestFeatureNameSpace,
  };

  const svg = container
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .attr('id', `${SomeID}_correlationMatrixSvg`);

  svg
    .append('rect')
    .attr('x', margin.left - cellSize / 2 - 2)
    .attr('y', margin.top - cellSize / 2 - 2)
    .attr('width', width + 2)
    .attr('height', height + 2)
    .attr('fill', 'none')
    .attr('stroke', 'black')
    .attr('stroke-opacity', 0.15);

  const mainGroup = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);
  const colnames = mainGroup.append('g');

  const colnamesEnter = colnames
    .selectAll('text')
    .data(featureNames)
    .enter();

  const upperNames = colnamesEnter
    .append('text')
    .attr('x', (d, i) => i * cellSize)
    .attr('y', -30)
    .attr('text-anchor', 'middle')
    .attr('font-weight', 700)
    .attr('opacity', 0)
    .attr('class', (_, i) => `colname colname-${i}`)
    .text((d) => truncate(d));

  const lowerNames = upperNames
    .clone(true)
    .attr('opacity', 1)
    .text((d) => truncate(d))
    .attr('x', 0)
    .attr('y', 0)
    .attr('font-weight', 400)
    .attr('text-anchor', 'start')
    .attr('opacity', 0.15)
    .attr('class', (_, i) => `lowercolname lowercolname-${i}`)
    .attr('transform', (d, i) => `translate(${i * cellSize - 5}, ${width - 8}) rotate(30)`)
    .append('title')
    .text((d: string) => d);

  for (let i = 0; i < featureNames.length; i += 1) {
    const rowGroup = mainGroup
      .append('g')
      .classed('row', true)
      .attr('transform', `translate(0, ${i * cellSize})`);
    // append feature name to row
    rowGroup
      .append('text')
      .attr('x', -cellSize / 2 - 10)
      .attr('class', 'rowname')
      .attr('text-anchor', 'end')
      .attr('dominant-baseline', 'middle')
      .text(truncate(featureNames[i]))
      .append('title')
      .text(featureNames[i]);
    for (let j = 0; j < featureNames.length; j += 1) {
      const cellGroup = rowGroup.append('g').attr('transform', `translate(${j * cellSize}, 0)`);
      const value = inputData.values[featureNames[i]][featureNames[j]];
      if (lowerOnly && j > i) {
        // eslint-disable-next-line no-continue
        continue;
      }
      if (addCircles) {
        cellGroup
          .append('circle')
          .attr('r', 0)
          .attr('fill', colorScale(value))
          .attr('stroke', 'black')
          .attr('stroke-width', 0)
          .attr('class', `cell cell-${i}-${j}`)
          .on('mouseover', function () {
            d3.select(this).attr('stroke-width', 1);
            d3.select(this.parentNode as SVGGElement).raise();
            d3.select(this.parentNode as SVGGElement)
              .selectAll('text.value')
              .transition()
              .duration(100)
              .attr('opacity', 1);
            rowGroup.select('text').attr('font-weight', 700);
            colnames.selectAll(`.lowercolname-${j}`).attr('opacity', 1);
          })
          .on('mouseout', function () {
            d3.select(this).attr('stroke-width', 0);
            d3.select(this.parentNode as SVGGElement)
              .selectAll('text')
              .lower();
            d3.select(this.parentNode as SVGGElement)
              .selectAll('.backdrop')
              .lower();
            d3.select(this.parentNode as SVGGElement)
              .selectAll('text.value')
              .transition()
              .duration(100)
              .attr('opacity', 0);
            rowGroup.select('text').attr('font-weight', 400);
            colnames.selectAll(`.lowercolname-${j}`).attr('opacity', 0.15);
          })
          .transition()
          .duration(() => 500 + Math.random() * 1000)
          .attr('r', radius(value));
      }
      cellGroup
        .append('text')
        .attr('class', 'value')
        .style('pointer-events', 'none')
        .attr('x', radius(value) + 5)
        .attr('y', 2)
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'middle')
        .attr('opacity', 0)
        .attr('fill', 'black')
        .text(value)
        .clone(true)
        .lower()
        .attr('class', 'value backdrop')
        .attr('stroke-linejoin', 'round')
        .attr('stroke-width', 4)
        .attr('stroke', 'white');
    }
  }
}

onMounted(() => {
  try {
    // @ts-ignore
    drawCorrelationMatrix(transformData(props.inputData), null);
  } catch (error) {
    console.error(error);
  }
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
