import { defaultApiClient } from './client';
import type {
  ObservabilityKPIs,
  SystemTopology,
  EventLifecycleTrace,
  KafkaPartitionLag,
  ParallelBranchLatency
} from '@/types/observability';

export class ObservabilityService {
  constructor(private client = defaultApiClient) {}

  public async getOverview(window = '1h', forceProbe = false): Promise<{ kpis: ObservabilityKPIs; platform_status: string }> {
    const res = await this.client.get('/observability/overview', { window, force_probe: forceProbe });
    return {
      kpis: {
        events_ingested: res.kpis?.events_ingested ?? 0,
        events_processed: res.kpis?.events_processed ?? 0,
        events_failed_dlq: res.kpis?.events_failed_dlq ?? 0,
        active_kafka_lag: res.kpis?.active_kafka_lag ?? 0,
        e2e_latency_p50_ms: res.kpis?.e2e_latency_p50_ms ?? 0,
        e2e_latency_p95_ms: res.kpis?.e2e_latency_p95_ms ?? 0,
        e2e_latency_p99_ms: res.kpis?.e2e_latency_p99_ms ?? 0,
        freshness_seconds: res.kpis?.freshness_seconds ?? 0,
        uptime_seconds: res.kpis?.uptime_seconds ?? 0
      },
      platform_status: res.platform_status || 'HEALTHY'
    };
  }

  public async getTopology(): Promise<SystemTopology> {
    const res = await this.client.get('/observability/topology');
    return {
      nodes: res.nodes || [],
      edges: res.edges || [],
      last_updated: res.last_updated || new Date().toISOString()
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
        current_offset: cg.current_offset ?? 0,
        log_end_offset: cg.log_end_offset ?? 0,
        lag: cg.lag ?? 0
      }))
    };
  }

  public async getStorageStatus(): Promise<any> {
    return await this.client.get('/observability/storage');
  }

  public async getLatencyPercentiles(): Promise<ParallelBranchLatency> {
    const res = await this.client.get('/observability/latency');
    return {
      serial_spine_ms: res.serial_spine_ms ?? 0,
      hot_branch_ms: res.hot_branch_ms ?? 0,
      olap_branch_ms: res.olap_branch_ms ?? 0,
      lakehouse_branch_ms: res.lakehouse_branch_ms ?? 0,
      serving_hot_e2e_ms: res.serving_hot_e2e_ms ?? 0,
      serving_olap_e2e_ms: res.serving_olap_e2e_ms ?? 0,
      serving_lakehouse_e2e_ms: res.serving_lakehouse_e2e_ms ?? 0,
      end_to_end_serving_ms: res.end_to_end_serving_ms ?? 0
    };
  }

  public async getTraces(limit = 20, mode?: string): Promise<EventLifecycleTrace[]> {
    const res = await this.client.get('/observability/traces', { limit, mode });
    const items = Array.isArray(res) ? res : res.traces || [];
    return items.map((t: any) => ({
      event_id: t.event_id || '',
      correlation_id: t.correlation_id || '',
      symbol: t.symbol || 'BTCUSDT',
      execution_mode: t.execution_mode || 'LIVE',
      final_status: t.final_status || 'UNKNOWN',
      timestamps: t.timestamps || {},
      latencies: t.latencies || {
        serial_spine_ms: 0,
        hot_branch_ms: 0,
        olap_branch_ms: 0,
        lakehouse_branch_ms: 0,
        serving_hot_e2e_ms: 0,
        serving_olap_e2e_ms: 0,
        serving_lakehouse_e2e_ms: 0,
        end_to_end_serving_ms: 0
      }
    }));
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

