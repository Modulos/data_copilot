export interface BarChartInput {
  data: Record<string, number>;
  others: number;
}

export interface BarChartOutput {
  label: string;
  value: number;
}

export function transformToLabelValuePairs(inputData: BarChartInput): BarChartOutput[] {
  let dataMapped = Object.entries(inputData.data).map(([k, v]) => ({ label: k, value: v }));

  if (inputData.others && inputData.others > 0) {
    dataMapped.push({
      label: 'Others',
      value: inputData.others,
    });
  }

  // sort dataMapped by value ascending
  dataMapped = dataMapped.sort((a, b) => b.value - a.value);

  return dataMapped;
}
