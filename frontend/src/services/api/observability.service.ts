import { defaultApiClient } from './client';
import type {
  ObservabilityKPIs,
  SystemTopology,
  EventLifecycleTrace,
  KafkaPartitionLag,
  ParallelBranchLatency
} from '@/types/observability';

function mapRawTrace(t: any): EventLifecycleTrace {
  const ts = t?.timestamps || {};
  const br = t?.latencies || t?.branch_latencies_ms || {};
  return {
    event_id: t?.event_id || '',
    correlation_id: t?.correlation_id || '',
    symbol: t?.symbol || 'BTCUSDT',
    execution_mode: t?.execution_mode || 'LIVE',
    final_status: t?.final_status || 'UNKNOWN',
    timestamps: {
      t0_collector_rx: ts.t0_collector_rx ?? ts.exchange_event_time ?? t?.exchange_event_time,
      t1_normalizer_done: ts.t1_normalizer_done ?? ts.ingested_at ?? t?.ingested_at,
      t2_kafka_published: ts.t2_kafka_published ?? ts.kafka_published_at ?? t?.kafka_published_at,
      t3_kafka_consumed: ts.t3_kafka_consumed ?? ts.kafka_consumed_at ?? t?.kafka_consumed_at,
      t4_redis_hot_written: ts.t4_redis_hot_written ?? ts.redis_written_at ?? t?.redis_written_at,
      t5_clickhouse_written: ts.t5_clickhouse_written ?? ts.clickhouse_written_at ?? t?.clickhouse_written_at,
      t6_bronze_archived: ts.t6_bronze_archived ?? ts.bronze_committed_at ?? t?.bronze_committed_at,
      t7_silver_merged: ts.t7_silver_merged ?? ts.silver_processed_at ?? t?.silver_processed_at,
      t8_gold_refreshed: ts.t8_gold_refreshed ?? ts.gold_loaded_at ?? t?.gold_loaded_at,
      t9_serving_ready: ts.t9_serving_ready ?? ts.serving_available_at ?? t?.serving_available_at
    },
    latencies: {
      serial_spine_ms: br.serial_spine_ms ?? 0,
      hot_branch_ms: br.hot_branch_ms ?? t?.hot_branch_ms ?? 0,
      olap_branch_ms: br.olap_branch_ms ?? t?.olap_branch_ms ?? 0,
      lakehouse_branch_ms: br.lakehouse_branch_ms ?? t?.lakehouse_branch_ms ?? 0,
      serving_hot_e2e_ms: br.serving_hot_e2e_ms ?? t?.serving_hot_e2e_ms ?? 0,
      serving_olap_e2e_ms: br.serving_olap_e2e_ms ?? t?.serving_olap_e2e_ms ?? 0,
      serving_lakehouse_e2e_ms: br.serving_lakehouse_e2e_ms ?? t?.serving_lakehouse_e2e_ms ?? 0,
      end_to_end_serving_ms: br.end_to_end_serving_ms ?? t?.end_to_end_serving_ms ?? 0
    }
  };
}

export function normalizeOverviewPayload(res: any): { kpis: ObservabilityKPIs; platform_status: string } {
  const k = res?.kpis || {};
  const e2e = k.e2e_latency_ms || {};
  const redisAgeMs = res?.freshness?.redis_hot_age_ms;
  const hasFailures = (k.events_failed_dlq ?? 0) > 0 || (k.events_dq_blocked ?? 0) > 0;
  return {
    kpis: {
      events_ingested: k.events_ingested ?? 0,
      events_processed: k.events_processed ?? 0,
      events_failed_dlq: k.events_failed_dlq ?? 0,
      active_kafka_lag: k.active_kafka_lag ?? k.kafka_total_lag ?? 0,
      e2e_latency_p50_ms: k.e2e_latency_p50_ms ?? e2e.p50 ?? 0,
      e2e_latency_p95_ms: k.e2e_latency_p95_ms ?? e2e.p95 ?? 0,
      e2e_latency_p99_ms: k.e2e_latency_p99_ms ?? e2e.p99 ?? 0,
      freshness_seconds:
        k.freshness_seconds ?? (typeof redisAgeMs === 'number' ? Number((redisAgeMs / 1000).toFixed(3)) : 0),
      uptime_seconds: k.uptime_seconds ?? 0
    },
    platform_status: res?.platform_status || (hasFailures ? 'DEGRADED' : 'HEALTHY')
  };
}

export { mapRawTrace };

export class ObservabilityService {
  constructor(private client = defaultApiClient) {}

  public async getOverview(window = '1h', forceProbe = false): Promise<{ kpis: ObservabilityKPIs; platform_status: string }> {
    const res = await this.client.get('/observability/overview', { window, force_probe: forceProbe });
    return normalizeOverviewPayload(res);
  }

  public async getTopology(): Promise<SystemTopology> {
    const res = await this.client.get('/observability/topology');
    const rawNodes = Array.isArray(res.nodes) ? res.nodes : [];
    return {
      nodes: rawNodes.map((n: any) => ({
        id: n.id || '',
        label: n.label || n.id || '',
        layer: n.layer || 'STREAMING',
        status: n.status || 'HEALTHY',
        metrics: n.metrics || {
          rate_per_sec: n.throughput_eps ?? 0,
          latency_p50_ms: n.latency_ms ?? 0,
          latency_p99_ms: n.latency_p95_ms ?? n.latency_ms ?? 0,
          error_rate_percent: n.errors && n.records ? Number(((n.errors / n.records) * 100).toFixed(2)) : 0,
          buffer_depth: n.lag
        },
        details: n
      })),
      edges: res.edges || [],
      last_updated: res.last_updated || res.generated_at_utc || new Date().toISOString()
    };
  }

  public async getKafkaLag(topic = 'market.raw.trades.v1'): Promise<{ brokers: any[]; consumer_groups: KafkaPartitionLag[] }> {
    const res = await this.client.get('/observability/kafka', { topic });
    const detail = res.selected_topic_detail || {};
    return {
      brokers: res.brokers || [],
      consumer_groups: (detail.consumer_groups || []).map((cg: any) => ({
        topic: cg.topic || topic,
        partition: cg.partition ?? 0,
        consumer_group: cg.consumer_group || '',
        current_offset: cg.current_offset ?? cg.committed_offset ?? 0,
        log_end_offset: cg.log_end_offset ?? cg.total_messages ?? 0,
        lag: cg.lag ?? 0
      }))
    };
  }

  public async getStorageStatus(): Promise<any> {
    return await this.client.get('/observability/storage');
  }

  public async getLatencyPercentiles(): Promise<ParallelBranchLatency> {
    const res = await this.client.get('/observability/latency');
    const bs = res.branch_stats || {};
    return {
      serial_spine_ms: res.serial_spine_ms ?? bs.serial_spine_ms?.p50 ?? 0,
      hot_branch_ms: res.hot_branch_ms ?? bs.hot_branch_ms?.p50 ?? 0,
      olap_branch_ms: res.olap_branch_ms ?? bs.olap_branch_ms?.p50 ?? 0,
      lakehouse_branch_ms: res.lakehouse_branch_ms ?? bs.lakehouse_branch_ms?.p50 ?? 0,
      serving_hot_e2e_ms: res.serving_hot_e2e_ms ?? bs.serving_hot_e2e_ms?.p50 ?? 0,
      serving_olap_e2e_ms: res.serving_olap_e2e_ms ?? bs.serving_olap_e2e_ms?.p50 ?? 0,
      serving_lakehouse_e2e_ms: res.serving_lakehouse_e2e_ms ?? bs.serving_lakehouse_e2e_ms?.p50 ?? 0,
      end_to_end_serving_ms: res.end_to_end_serving_ms ?? bs.end_to_end_serving_ms?.p50 ?? 0
    };
  }

  public async getTraces(limit = 20, mode?: string): Promise<EventLifecycleTrace[]> {
    const res = await this.client.get('/observability/traces', { limit, mode });
    const items = Array.isArray(res) ? res : res.traces || [];
    return items.map(mapRawTrace);
  }

  public async triggerLiveProbe(symbol = 'BTCUSDT', interval = '1m', fetchBinance = false): Promise<any> {
    return await this.client.post('/observability/live/probe', {
      symbol,
      interval,
      limit: 10,
      fetch_binance: fetchBinance
    });
  }

  public async triggerDemoEmit(action = 'emit_batch', symbol = 'BTCUSDT', count = 5): Promise<any> {
    return await this.client.post('/observability/demo/emit', {
      action,
      symbol,
      count
    });
  }

  public async setStreamControl(mode: 'LIVE' | 'STRESS_50' | 'STRESS_200' | 'PAUSED'): Promise<any> {
    return await this.client.post('/observability/stream/control', { mode });
  }
}

export const observabilityService = new ObservabilityService();

