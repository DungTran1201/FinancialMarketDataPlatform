import { defaultApiClient } from './client';
import type { DatasetCatalogItem, DataQualityCheckResult, LineageEdge } from '@/types/catalog';

export class CatalogService {
  constructor(private client = defaultApiClient) {}

  public async getDatasets(): Promise<DatasetCatalogItem[]> {
    const [lineageRes, storageRes] = await Promise.all([
      this.client.get('/data-platform/v01/lineage'),
      this.client.get('/observability/storage').catch(() => ({}))
    ]);
    const items = Array.isArray(lineageRes) ? lineageRes : lineageRes.datasets || [];
    const lh = storageRes?.lakehouse || {};
    const chRows = storageRes?.clickhouse_warehouse?.total_rows ?? 0;
    const redisRows = storageRes?.redis_hot_state?.price_keys_count ?? 0;
    const layerMap: Record<string, DatasetCatalogItem['layer']> = {
      BRONZE: 'BRONZE',
      SILVER: 'SILVER',
      GOLD: 'GOLD',
      STREAM: 'KAFKA',
      HOT: 'HOT_CACHE'
    };
    const formatMap: Record<string, DatasetCatalogItem['storage_format']> = {
      BRONZE: 'PARQUET',
      SILVER: 'ICEBERG_V2',
      GOLD: 'PARQUET',
      OLAP: 'CLICKHOUSE_REPLACING_MERGE_TREE',
      HOT: 'REDIS_HASH',
      STREAM: 'JSON_KAFKA'
    };
    return items.map((d: any) => {
      const rawLayer = String(d.layer || 'SILVER').toUpperCase();
      const natKeys: string[] = Array.isArray(d.natural_key) ? d.natural_key : [];
      const records =
        rawLayer === 'BRONZE'
          ? (lh.bronze?.total_rows ?? 0)
          : rawLayer === 'SILVER'
            ? (lh.silver?.total_rows ?? 0)
            : rawLayer === 'GOLD'
              ? (lh.gold?.total_rows ?? 0)
              : rawLayer === 'OLAP'
                ? chRows
                : rawLayer === 'HOT'
                  ? redisRows
                  : 0;
      const bytes = rawLayer === 'BRONZE' ? (lh.bronze?.total_bytes ?? 0) : 0;
      return {
        id: d.dataset_id || d.id || d.name,
        name: d.dataset_id || d.name,
        layer: layerMap[rawLayer] || 'SILVER',
        storage_format: formatMap[rawLayer] || 'ICEBERG_V2',
        retention: d.retention_policy || d.retention || '90 days',
        update_frequency: d.freshness_slo_seconds ? `SLO ${d.freshness_slo_seconds}s` : 'Continuous',
        total_records: records,
        size_bytes: bytes,
        last_ingested_at: new Date().toISOString(),
        schema:
          d.schema ||
          natKeys.map((k: string) => ({
            name: k,
            type: 'string',
            nullable: false,
            is_natural_key: true
          }))
      };
    });
  }

  public async getLineage(): Promise<{ nodes: string[]; edges: LineageEdge[] }> {
    const res = await this.client.get('/data-platform/v01/lineage');
    const datasets = Array.isArray(res?.datasets) ? res.datasets : [];
    const rawEdges = Array.isArray(res?.lineage_edges) ? res.lineage_edges : res?.edges || [];
    const edges: LineageEdge[] = rawEdges.map((e: any) => ({
      from_dataset: e.from_dataset || e.upstream_dataset || '',
      to_dataset: e.to_dataset || e.downstream_dataset || '',
      transformation: e.transformation || e.transformation_job || ''
    }));
    const nodes: string[] =
      datasets.length > 0
        ? datasets.map((d: any) => String(d.dataset_id || d.name))
        : ['Binance WS/REST', 'Kafka (market.raw.*.v1)', 'Redis Hot Cache', 'MinIO Bronze', 'Silver Iceberg', 'Gold dbt Marts', 'ClickHouse OLAP', 'FastAPI Serving'];
    return {
      nodes,
      edges:
        edges.length > 0
          ? edges
          : [
              { from_dataset: 'exchange.binance.spot_api', to_dataset: 'kafka.market.raw.klines.v1', transformation: 'collector-rest-and-ws' },
              { from_dataset: 'kafka.market.raw.klines.v1', to_dataset: 'redis.market.hot_state.v1', transformation: 'consumer-hot-redis' },
              { from_dataset: 'kafka.market.raw.klines.v1', to_dataset: 'clickhouse.market_data.klines_1m', transformation: 'consumer-analytics-ch' },
              { from_dataset: 'kafka.market.raw.klines.v1', to_dataset: 'lakehouse.bronze.raw_events', transformation: 'consumer-lakehouse-bronze' }
            ]
    };
  }

  public async getDataQualityReport(): Promise<DataQualityCheckResult[]> {
    const res = await this.client.get('/observability/storage');
    const items = Array.isArray(res) ? res : res.dq_rules || res.checks || [];
    return items.map((c: any) => ({
      rule_id: c.rule_id || 'DQ-001',
      rule_name: c.rule_name || c.rule || 'Positive Financial Numbers',
      dataset_id: c.dataset_id || c.dataset || 'silver.market_klines',
      status: c.status || 'PASSED',
      evaluated_records: c.evaluated_records ?? (res?.lakehouse?.silver?.total_rows || 0),
      violated_records: c.violated_records ?? 0,
      last_run_at: c.last_run_at || new Date().toISOString(),
      sample_violation: c.sample_violation
    }));
  }
}

export const catalogService = new CatalogService();

