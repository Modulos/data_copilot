import * as d3 from 'd3';

export function addEmptySvgToContainer(containerName: string) {
  const width = 300;
  const height = 280;

  const container = d3.select(`#${containerName}`);

  const svg = container
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  const defs = svg.append('defs');
  const linearGradient = defs.append('linearGradient').attr('id', 'linear-gradient');

  linearGradient
    .attr('x1', '0%')
    .attr('y1', '0%')
    .attr('x2', '0%')
    .attr('y2', '100%');
  linearGradient
    .append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#1C9ED6');
  linearGradient
    .append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#F4FAFD');

  return svg;
}

export function getRandomId() {
  const letters = 'abcdefghijklmnopqrstuvwxyz';
  const array = new Uint32Array(8);
  window.crypto.getRandomValues(array);
  let randomID = letters[Math.floor(Math.random() * letters.length)];
  for (let i = 0; i < array.length; i += 1) {
    randomID += (i < 1 || i > 4 ? '' : '-') + array[i].toString(36).slice(-8);
  }
  return randomID;
}
