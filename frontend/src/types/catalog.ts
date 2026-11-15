export type MedallionLayer = 'BRONZE' | 'SILVER' | 'GOLD' | 'KAFKA' | 'HOT_CACHE';

export interface SchemaField {
  name: string;
  type: string;
  nullable: boolean;
  is_natural_key?: boolean;
  description?: string;
}

export interface DatasetCatalogItem {
  id: string;
  name: string;
  layer: MedallionLayer;
  storage_format: 'PARQUET' | 'ICEBERG_V2' | 'CLICKHOUSE_REPLACING_MERGE_TREE' | 'REDIS_HASH' | 'JSON_KAFKA';
  retention: string;
  update_frequency: string;
  total_records: number;
  size_bytes: number;
  last_ingested_at: string;
  schema: SchemaField[];
}

export interface DataQualityCheckResult {
  rule_id: string;
  rule_name: string;
  dataset_id: string;
  status: 'PASSED' | 'FAILED' | 'WARNING';
  evaluated_records: number;
  violated_records: number;
  last_run_at: string;
  sample_violation?: string;
}

export interface LineageEdge {
  from_dataset: string;
  to_dataset: string;
  transformation: string;
}

