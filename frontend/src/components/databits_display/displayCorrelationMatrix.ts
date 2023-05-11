export interface CorrelationMatrixInput {
  feature_names: string[];
  measure: string;
  values: Record<string, Record<string, number>>;
  warnings: string[];
}
