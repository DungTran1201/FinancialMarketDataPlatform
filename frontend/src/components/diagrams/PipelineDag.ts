import type { SystemTopology, TopologyNode } from '@/types/observability';
import { createElement } from '@/utils/dom';

export class PipelineDag {
  private container: HTMLElement;
  private onNodeClick?: (node: TopologyNode) => void;
  private topology: SystemTopology | null = null;

  constructor(container: HTMLElement, onNodeClick?: (node: TopologyNode) => void) {
    this.container = container;
    this.onNodeClick = onNodeClick;
  }

  public setTopology(topology: SystemTopology): void {
    this.topology = topology;
    this.render();
  }

  public render(): void {
    this.container.innerHTML = '';

    const wrapper = createElement('div', {
      style: {
        width: '100%',
        overflowX: 'auto',
        padding: '16px 0',
        backgroundColor: 'var(--bg-app)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)'
      }
    });

    // High quality interactive SVG DAG
    const svg = `
    <svg viewBox="0 0 1150 420" width="100%" height="420" xmlns="http://www.w3.org/2000/svg" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
      <defs>
        <!-- Gradients -->
        <linearGradient id="gradIngest" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#1e293b"/>
          <stop offset="100%" stop-color="#0f172a"/>
        </linearGradient>
        <linearGradient id="gradKafka" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#0369a1"/>
          <stop offset="100%" stop-color="#075985"/>
        </linearGradient>
        <linearGradient id="gradRedis" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#b91c1c"/>
          <stop offset="100%" stop-color="#7f1d1d"/>
        </linearGradient>
        <linearGradient id="gradCH" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#d97706"/>
          <stop offset="100%" stop-color="#b45309"/>
        </linearGradient>
        <linearGradient id="gradLake" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#047857"/>
          <stop offset="100%" stop-color="#065f46"/>
        </linearGradient>
        <linearGradient id="gradServing" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#4338ca"/>
          <stop offset="100%" stop-color="#3730a3"/>
        </linearGradient>

        <!-- Glow filter -->
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      <!-- Connection Lines with Flow Pulses -->
      <g stroke="#3b82f6" stroke-width="2" fill="none" opacity="0.6">
        <!-- Ingestion to Kafka -->
        <path d="M 180 210 L 260 210" class="anim-flow-line" />

        <!-- Kafka to 3 Parallel Sinks -->
        <!-- Branch 1: Kafka -> Redis (Hot) -->
        <path d="M 420 180 C 470 180, 480 90, 540 90" class="anim-flow-line" stroke="#ef4444" />
        <!-- Branch 2: Kafka -> ClickHouse (OLAP) -->
        <path d="M 420 210 L 540 210" class="anim-flow-line" stroke="#f59e0b" />
        <!-- Branch 3: Kafka -> Lakehouse (MinIO) -->
        <path d="M 420 240 C 470 240, 480 330, 540 330" class="anim-flow-line" stroke="#10b981" />

        <!-- Lakehouse Pipeline: Bronze -> Silver -> Gold -->
        <path d="M 680 330 L 730 330" class="anim-flow-line" stroke="#10b981" />
        <path d="M 850 330 L 900 330" class="anim-flow-line" stroke="#10b981" />

        <!-- Sinks to Serving Plane -->
        <!-- Redis -> Serving -->
        <path d="M 680 90 C 780 90, 840 180, 930 180" class="anim-flow-line" stroke="#ef4444" />
        <!-- ClickHouse -> Serving -->
        <path d="M 680 210 L 930 210" class="anim-flow-line" stroke="#f59e0b" />
        <!-- Gold -> Serving -->
        <path d="M 1020 310 C 1020 260, 990 230, 970 230" class="anim-flow-line" stroke="#10b981" />

        <!-- Serving -> Frontend / Experience Layer -->
        <path d="M 1070 210 L 1110 210" stroke="#3b82f6" stroke-dasharray="4,4" />
      </g>

      <!-- Latency & Protocol Annotations -->
      <g font-size="10" font-family="monospace" fill="#94a3b8" text-anchor="middle">
        <text x="220" y="200">WS Raw (~0.2ms)</text>
        <text x="480" y="115" fill="#ef4444">Monotonic Lua (sub-15ms)</text>
        <text x="480" y="200" fill="#f59e0b">Micro-batch (1s/5k)</text>
        <text x="480" y="315" fill="#10b981">Append Parquet</text>
        <text x="705" y="320">PySpark</text>
        <text x="875" y="320">dbt Marts</text>
        <text x="850" y="125" fill="#60a5fa">Sub-15ms Read</text>
      </g>

      <!-- 1. Node: Collector (Binance Spot) -->
      <g id="node-collector" cursor="pointer" transform="translate(40, 160)">
        <rect width="140" height="100" rx="8" fill="url(#gradIngest)" stroke="#24344d" stroke-width="2" />
        <circle cx="25" cy="28" r="6" fill="#10b981" class="anim-pulse-green" />
        <text x="40" y="32" font-size="13" font-weight="bold" fill="#f8fafc">Collector WS</text>
        <text x="20" y="58" font-size="10" fill="#94a3b8">Binance Spot</text>
        <text x="20" y="74" font-size="10" fill="#94a3b8">Rate: 1,200 msg/s</text>
        <text x="20" y="90" font-size="9" fill="#3b82f6">P50: 0.2ms</text>
      </g>

      <!-- 2. Node: Apache Kafka (KRaft) -->
      <g id="node-kafka" cursor="pointer" transform="translate(260, 140)">
        <rect width="160" height="140" rx="8" fill="url(#gradKafka)" stroke="#38bdf8" stroke-width="2" />
        <circle cx="25" cy="28" r="6" fill="#10b981" class="anim-pulse-green" />
        <text x="40" y="32" font-size="14" font-weight="bold" fill="#f8fafc">Kafka KRaft</text>
        <text x="20" y="60" font-size="10" fill="#e0f2fe">6 Topics | Partitioned</text>
        <text x="20" y="80" font-size="10" fill="#e0f2fe">Broker 1: Active</text>
        <text x="20" y="96" font-size="10" fill="#f87171">B2/B3: Unavailable</text>
        <text x="20" y="118" font-size="9" font-family="monospace" fill="#38bdf8">Lag: 0 | P50: 0.3ms</text>
      </g>

      <!-- 3. Parallel Sink Branch 1: Redis 7 (Hot Path) -->
      <g id="node-redis" cursor="pointer" transform="translate(540, 40)">
        <rect width="140" height="100" rx="8" fill="url(#gradRedis)" stroke="#f87171" stroke-width="2" />
        <circle cx="25" cy="28" r="6" fill="#10b981" class="anim-pulse-green" />
        <text x="40" y="32" font-size="13" font-weight="bold" fill="#f8fafc">Redis 7 (Hot)</text>
        <text x="20" y="56" font-size="10" fill="#fecaca">Order Book & Price</text>
        <text x="20" y="72" font-size="10" fill="#fecaca">Monotonic Lua Check</text>
        <text x="20" y="90" font-size="9" font-family="monospace" fill="#f87171">Query: sub-15ms</text>
      </g>

      <!-- 4. Parallel Sink Branch 2: ClickHouse (OLAP) -->
      <g id="node-clickhouse" cursor="pointer" transform="translate(540, 160)">
        <rect width="140" height="100" rx="8" fill="url(#gradCH)" stroke="#fbbf24" stroke-width="2" />
        <circle cx="25" cy="28" r="6" fill="#10b981" class="anim-pulse-green" />
        <text x="40" y="32" font-size="13" font-weight="bold" fill="#f8fafc">ClickHouse OLAP</text>
        <text x="20" y="56" font-size="10" fill="#fef3c7">ReplacingMergeTree</text>
        <text x="20" y="72" font-size="10" fill="#fef3c7">1s Micro-batches</text>
        <text x="20" y="90" font-size="9" font-family="monospace" fill="#fbbf24">OLAP: sub-100ms</text>
      </g>

      <!-- 5. Parallel Sink Branch 3: MinIO Lakehouse (Bronze) -->
      <g id="node-bronze" cursor="pointer" transform="translate(540, 280)">
        <rect width="140" height="100" rx="8" fill="url(#gradLake)" stroke="#34d399" stroke-width="2" />
        <circle cx="25" cy="28" r="6" fill="#10b981" class="anim-pulse-green" />
        <text x="40" y="32" font-size="13" font-weight="bold" fill="#f8fafc">Bronze (MinIO)</text>
        <text x="20" y="56" font-size="10" fill="#d1fae5">Parquet Append-Only</text>
        <text x="20" y="72" font-size="10" fill="#d1fae5">Audit Trail Archive</text>
        <text x="20" y="90" font-size="9" font-family="monospace" fill="#34d399">Raw Storage</text>
      </g>

      <!-- 6. Lakehouse Silver (Iceberg v2) -->
      <g id="node-silver" cursor="pointer" transform="translate(730, 280)">
        <rect width="120" height="100" rx="8" fill="url(#gradLake)" stroke="#34d399" stroke-width="2" />
        <circle cx="20" cy="28" r="5" fill="#10b981" />
        <text x="32" y="32" font-size="12" font-weight="bold" fill="#f8fafc">Silver (Iceberg)</text>
        <text x="15" y="56" font-size="10" fill="#d1fae5">PySpark Merge</text>
        <text x="15" y="72" font-size="10" fill="#d1fae5">Deduplicated</text>
        <text x="15" y="90" font-size="9" font-family="monospace" fill="#34d399">ACID v2</text>
      </g>

      <!-- 7. Lakehouse Gold (dbt Marts) -->
      <g id="node-gold" cursor="pointer" transform="translate(900, 280)">
        <rect width="120" height="100" rx="8" fill="url(#gradLake)" stroke="#34d399" stroke-width="2" />
        <circle cx="20" cy="28" r="5" fill="#10b981" />
        <text x="32" y="32" font-size="12" font-weight="bold" fill="#f8fafc">Gold (dbt)</text>
        <text x="15" y="56" font-size="10" fill="#d1fae5">Curated Marts</text>
        <text x="15" y="72" font-size="10" fill="#d1fae5">Multi-Timeframe</text>
        <text x="15" y="90" font-size="9" font-family="monospace" fill="#34d399">Business Ready</text>
      </g>

      <!-- 8. Serving Plane (FastAPI Gateway) -->
      <g id="node-serving" cursor="pointer" transform="translate(930, 160)">
        <rect width="140" height="100" rx="8" fill="url(#gradServing)" stroke="#818cf8" stroke-width="2" />
        <circle cx="25" cy="28" r="6" fill="#10b981" class="anim-pulse-green" />
        <text x="40" y="32" font-size="13" font-weight="bold" fill="#f8fafc">FastAPI Serving</text>
        <text x="20" y="56" font-size="10" fill="#e0e7ff">Clean Architecture</text>
        <text x="20" y="72" font-size="10" fill="#e0e7ff">8 Domain Contexts</text>
        <text x="20" y="90" font-size="9" font-family="monospace" fill="#818cf8">REST / SSE / WS</text>
      </g>
    </svg>
    `;

    wrapper.innerHTML = svg;
    this.container.appendChild(wrapper);

    // Bind click events on SVG nodes
    const nodeMap: Record<string, Partial<TopologyNode>> = {
      'node-collector': { id: 'collector_ws', label: 'WebSocket Collector (Binance Spot)', layer: 'INGESTION', status: 'HEALTHY' },
      'node-kafka': { id: 'kafka_cluster', label: 'Apache Kafka Cluster (KRaft)', layer: 'STREAMING', status: 'HEALTHY' },
      'node-redis': { id: 'redis_hot', label: 'Redis 7 Hot Store', layer: 'STORAGE', status: 'HEALTHY' },
      'node-clickhouse': { id: 'clickhouse_olap', label: 'ClickHouse OLAP Engine', layer: 'STORAGE', status: 'HEALTHY' },
      'node-bronze': { id: 'minio_bronze', label: 'MinIO Bronze Parquet Archive', layer: 'STORAGE', status: 'HEALTHY' },
      'node-silver': { id: 'silver_iceberg', label: 'Silver Iceberg v2 Clean Layer', layer: 'STORAGE', status: 'HEALTHY' },
      'node-gold': { id: 'gold_marts', label: 'Gold Layer dbt Marts', layer: 'STORAGE', status: 'HEALTHY' },
      'node-serving': { id: 'fastapi_serving', label: 'FastAPI Modular Monolith (Plane B)', layer: 'SERVING', status: 'HEALTHY' }
    };

    for (const [nodeId, partial] of Object.entries(nodeMap)) {
      const el = wrapper.querySelector(`#${nodeId}`);
      if (el) {
        el.addEventListener('click', () => {
          if (this.onNodeClick) {
            const fullNode = (this.topology?.nodes || []).find(n => n.id === partial.id) || {
              id: partial.id!,
              label: partial.label!,
              layer: partial.layer!,
              status: partial.status!,
              metrics: { rate_per_sec: 1200, latency_p50_ms: 0.5, latency_p99_ms: 2.1, error_rate_percent: 0 }
            };
            this.onNodeClick(fullNode);
          }
        });
      }
    }
  }
}

