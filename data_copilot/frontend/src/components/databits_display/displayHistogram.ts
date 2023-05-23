export interface HistogramInput {
  values: number[];
  bins: number[];
}

export function transformToBinValuePairs(inputData: HistogramInput) {
  const dataMapped = inputData.bins.map((d, i) => {
    if (i === 0) {
      return [d, inputData.values[0]];
    }
    return [d, inputData.values[i - 1]];
  });
  return dataMapped;
}
