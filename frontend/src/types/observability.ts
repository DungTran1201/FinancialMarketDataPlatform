export interface ObservabilityKPIs {
  events_ingested: number;
  events_processed: number;
  events_failed_dlq: number;
  active_kafka_lag: number;
  e2e_latency_p50_ms: number;
  e2e_latency_p95_ms: number;
  e2e_latency_p99_ms: number;
  freshness_seconds: number;
  uptime_seconds: number;
}

export interface NodeMetrics {
  rate_per_sec: number;
  latency_p50_ms: number;
  latency_p99_ms: number;
  error_rate_percent: number;
  buffer_depth?: number;
}

export interface TopologyNode {
  id: string;
  label: string;
  layer: 'INGESTION' | 'STREAMING' | 'STORAGE' | 'SERVING';
  status: 'HEALTHY' | 'DEGRADED' | 'UNAVAILABLE' | 'PAUSED';
  metrics: NodeMetrics;
  details?: Record<string, any>;
}

export interface TopologyEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  protocol: 'WEBSOCKET' | 'KAFKA' | 'TCP' | 'HTTP' | 'INTERNAL';
  status: 'ACTIVE' | 'IDLE' | 'BLOCKED';
  throughput_msg_sec: number;
}

export interface SystemTopology {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  last_updated: string;
}

export interface ParallelBranchLatency {
  serial_spine_ms: number;
  hot_branch_ms: number;
  olap_branch_ms: number;
  lakehouse_branch_ms: number;
  serving_hot_e2e_ms: number;
  serving_olap_e2e_ms: number;
  serving_lakehouse_e2e_ms: number;
  end_to_end_serving_ms: number;
}

export interface EventLifecycleTrace {
  event_id: string;
  correlation_id: string;
  symbol: string;
  execution_mode: 'LIVE' | 'DEMO';
  final_status: string;
  timestamps: {
    t0_collector_rx?: string;
    t1_normalizer_done?: string;
    t2_kafka_published?: string;
    t3_kafka_consumed?: string;
    t4_redis_hot_written?: string;
    t5_clickhouse_written?: string;
    t6_bronze_archived?: string;
    t7_silver_merged?: string;
    t8_gold_refreshed?: string;
    t9_serving_ready?: string;
  };
  latencies: ParallelBranchLatency;
}

export interface KafkaBrokerStatus {
  id: number;
  address: string;
  role: 'CONTROLLER' | 'BROKER' | 'COMBINED';
  status: 'HEALTHY' | 'UNAVAILABLE';
}

export interface KafkaPartitionLag {
  topic: string;
  partition: number;
  consumer_group: string;
  current_offset: number;
  log_end_offset: number;
  lag: number;
}

