import { createElement } from '@/utils/dom';
import { PipelineDag } from '@/components/diagrams/PipelineDag';
import { LatencyHistogram } from '@/components/charts/LatencyHistogram';
import { createDataTable } from '@/components/tables/DataTable';
import { createBadge } from '@/components/ui/Badge';
import { Drawer } from '@/components/ui/Drawer';
import { observabilityStore } from '@/stores/observability.store';
import { observabilityService } from '@/services/api/observability.service';
import type { TopologyNode, EventLifecycleTrace, KafkaPartitionLag } from '@/types/observability';
import { formatLatency, formatNumber, formatUtcTime } from '@/utils/formatters';

export class DataFlowModule {
  private element: HTMLElement;
  private unsubscribe?: () => void;
  private dagContainer!: HTMLElement;
  private latencyContainer!: HTMLElement;
  private tracesContainer!: HTMLElement;
  private kafkaContainer!: HTMLElement;
  private pipelineDag!: PipelineDag;
  private latencyHistogram!: LatencyHistogram;
  private activeDrawer: Drawer | null = null;
  private kafkaLags: KafkaPartitionLag[] = [];

  constructor() {
    this.element = createElement('div', { className: 'data-flow-module anim-fade-in' });
  }

  public mount(parent: HTMLElement): void {
    parent.appendChild(this.element);
    this.buildLayout();

    this.unsubscribe = observabilityStore.subscribe((state) => {
      if (state.topology) {
        this.pipelineDag.setTopology(state.topology);
      }
      this.latencyHistogram.setData(state.latencies);
      this.renderTraces(state.traces);
    });

    this.loadKafkaLag();
    observabilityStore.loadInitial();
    observabilityStore.initSseStream();
  }

  public unmount(): void {
    if (this.activeDrawer) {
      this.activeDrawer.close();
      this.activeDrawer = null;
    }
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = undefined;
    }
    if (this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }

  private async loadKafkaLag(): Promise<void> {
    try {
      const res = await observabilityService.getKafkaLag('market.raw.trades.v1');
      this.kafkaLags = res.consumer_groups;
      this.renderKafkaSection();
    } catch {}
  }

  private buildLayout(): void {
    this.element.innerHTML = '';

    // Title & Description
    const header = createElement('div', { style: { marginBottom: '20px' } });
    header.innerHTML = `
      <h2 style="font-size: 1.25rem; font-weight: 700;">Data Flow & Parallel-Branch Pipeline Observatory</h2>
      <p style="font-size: 0.8rem; color: var(--text-muted);">
        Interactive visualization of Exchange -> Ingestion -> Kafka KRaft -> Parallel Sinks (Redis || ClickHouse || Lakehouse) -> Serving.
      </p>
    `;
    this.element.appendChild(header);

    // Section 1: Interactive SVG DAG
    const dagSection = createElement('div', { style: { marginBottom: '24px' } });
    const dagCard = createElement('div', { className: 'card' });
    dagCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Interactive Data Platform DAG (12 Stages)</span>
        <span class="card-subtitle">Click any node to inspect active rates, buffers, and latency</span>
      </div>
    `;
    this.dagContainer = createElement('div');
    dagCard.appendChild(this.dagContainer);
    dagSection.appendChild(dagCard);
    this.element.appendChild(dagSection);

    this.pipelineDag = new PipelineDag(this.dagContainer, (node) => this.openNodeDrawer(node));

    // Section 2: Two Column Grid (Latency Histogram + Kafka Lag Table)
    const grid2Col = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '20px',
        marginBottom: '24px'
      }
    });

    this.latencyContainer = createElement('div');
    grid2Col.appendChild(this.latencyContainer);
    this.latencyHistogram = new LatencyHistogram(this.latencyContainer);

    // Kafka Lag Container
    this.kafkaContainer = createElement('div');
    grid2Col.appendChild(this.kafkaContainer);
    this.element.appendChild(grid2Col);

    // Section 3: Event Lifecycle Tracing Table
    const traceSection = createElement('div');
    const traceCard = createElement('div', { className: 'card' });
    traceCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">10-Timestamp Event Lifecycle Traces (Live Stream)</span>
        <span class="card-subtitle">Trace event propagation across parallel sink branches</span>
      </div>
    `;
    this.tracesContainer = createElement('div');
    traceCard.appendChild(this.tracesContainer);
    traceSection.appendChild(traceCard);
    this.element.appendChild(traceSection);
  }

  private renderKafkaSection(): void {
    this.kafkaContainer.innerHTML = '';
    const card = createElement('div', { className: 'card' });
    card.innerHTML = `
      <div class="card-header">
        <span class="card-title">Kafka Cluster & Consumer Group Lag</span>
        <span class="badge badge-warning">1-Node KRaft Active (B2/B3 Down)</span>
      </div>
    `;

    const table = createDataTable<KafkaPartitionLag>({
      columns: [
        { key: 'consumer_group', header: 'Consumer Group' },
        { key: 'partition', header: 'Part', className: 'font-mono' },
        { key: 'current_offset', header: 'Offset', className: 'font-mono' },
        {
          key: 'lag',
          header: 'Lag',
          render: (row) => {
            const variant = row.lag === 0 ? 'success' : row.lag < 100 ? 'warning' : 'danger';
            return createBadge(`${row.lag} msg`, variant);
          }
        }
      ],
      data: this.kafkaLags,
      emptyMessage: 'No active consumer groups detected'
    });

    card.appendChild(table);
    this.kafkaContainer.appendChild(card);
  }

  private renderTraces(traces: EventLifecycleTrace[]): void {
    this.tracesContainer.innerHTML = '';
    const table = createDataTable<EventLifecycleTrace>({
      columns: [
        {
          key: 'event_id',
          header: 'Event ID',
          className: 'font-mono',
          render: (row) => row.event_id ? row.event_id.substring(0, 12) + '...' : '—'
        },
        { key: 'symbol', header: 'Symbol' },
        {
          key: 'execution_mode',
          header: 'Mode',
          render: (row) => createBadge(row.execution_mode, row.execution_mode === 'LIVE' ? 'info' : 'warning')
        },
        {
          key: 'final_status',
          header: 'Status',
          render: (row) => createBadge(row.final_status, row.final_status.includes('SERVING') ? 'success' : 'neutral')
        },
        {
          key: 'end_to_end_serving_ms',
          header: 'E2E Latency',
          className: 'font-mono',
          render: (row) => formatLatency(row.latencies.end_to_end_serving_ms)
        },
        {
          key: 'created',
          header: 'Timestamp (UTC)',
          className: 'font-mono',
          render: (row) => formatUtcTime(row.timestamps.t0_collector_rx)
        }
      ],
      data: traces.slice(0, 10),
      onRowClick: (trace) => this.openTraceDrawer(trace),
      emptyMessage: 'No trace events recorded. Emit a demo batch or start ingestion.'
    });

    this.tracesContainer.appendChild(table);
  }

  private openNodeDrawer(node: TopologyNode): void {
    if (this.activeDrawer) this.activeDrawer.close();

    this.activeDrawer = new Drawer({
      title: node.label,
      onClose: () => { this.activeDrawer = null; }
    });

    const content = createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: '16px' } });
    content.innerHTML = `
      <div style="display: flex; gap: 8px;">
        ${createBadge(node.layer, 'info').outerHTML}
        ${createBadge(node.status, node.status === 'HEALTHY' ? 'success' : 'danger').outerHTML}
      </div>

      <div class="card" style="margin-top: 10px;">
        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; margin-bottom: 8px;">
          Runtime Metrics
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.85rem;">
          <div>
            <div style="color: var(--text-muted);">Throughput</div>
            <div class="font-mono" style="font-weight: 700; font-size: 1.1rem;">${formatNumber(node.metrics.rate_per_sec, 0)} msg/s</div>
          </div>
          <div>
            <div style="color: var(--text-muted);">P50 Latency</div>
            <div class="font-mono" style="font-weight: 700; font-size: 1.1rem;">${formatLatency(node.metrics.latency_p50_ms)}</div>
          </div>
          <div>
            <div style="color: var(--text-muted);">P99 Latency</div>
            <div class="font-mono" style="font-weight: 700; font-size: 1.1rem;">${formatLatency(node.metrics.latency_p99_ms)}</div>
          </div>
          <div>
            <div style="color: var(--text-muted);">Error Rate</div>
            <div class="font-mono" style="font-weight: 700; font-size: 1.1rem; color: ${node.metrics.error_rate_percent === 0 ? '#10b981' : '#ef4444'};">
              ${node.metrics.error_rate_percent.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; margin-bottom: 8px;">
          Architectural Boundary & Invariant
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.5;">
          ${this.getNodeDescription(node.id)}
        </p>
      </div>
    `;

    this.activeDrawer.setContent(content);
    this.activeDrawer.open();
  }

  private openTraceDrawer(trace: EventLifecycleTrace): void {
    if (this.activeDrawer) this.activeDrawer.close();

    this.activeDrawer = new Drawer({
      title: `Event Trace: ${trace.symbol}`,
      onClose: () => { this.activeDrawer = null; }
    });

    const content = createElement('div', { style: { display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.8rem' } });
    content.innerHTML = `
      <div style="display: flex; gap: 8px;">
        ${createBadge(trace.execution_mode, trace.execution_mode === 'LIVE' ? 'info' : 'warning').outerHTML}
        ${createBadge(trace.final_status, 'success').outerHTML}
      </div>

      <div class="card">
        <div style="color: var(--text-muted); font-size: 0.7rem; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">Event ID</div>
        <div class="font-mono" style="word-break: break-all; color: var(--text-primary); font-size: 0.75rem;">${trace.event_id}</div>
      </div>

      <div class="card">
        <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 8px;">10 Timestamp Milestones</div>
        <div style="display: flex; flex-direction: column; gap: 6px; font-family: var(--font-mono); font-size: 0.75rem;">
          <div><span style="color: var(--text-muted);">t0 Collector RX:</span> ${formatUtcTime(trace.timestamps.t0_collector_rx)}</div>
          <div><span style="color: var(--text-muted);">t1 Normalizer Done:</span> ${formatUtcTime(trace.timestamps.t1_normalizer_done)}</div>
          <div><span style="color: var(--text-muted);">t2 Kafka Published:</span> ${formatUtcTime(trace.timestamps.t2_kafka_published)}</div>
          <div><span style="color: var(--text-muted);">t3 Kafka Consumed:</span> ${formatUtcTime(trace.timestamps.t3_kafka_consumed)}</div>
          <div><span style="color: var(--text-muted);">t4 Redis Hot:</span> ${formatUtcTime(trace.timestamps.t4_redis_hot_written)}</div>
          <div><span style="color: var(--text-muted);">t5 ClickHouse Written:</span> ${formatUtcTime(trace.timestamps.t5_clickhouse_written)}</div>
          <div><span style="color: var(--text-muted);">t6 Bronze Archive:</span> ${formatUtcTime(trace.timestamps.t6_bronze_archived)}</div>
          <div><span style="color: var(--text-muted);">t7 Silver Merged:</span> ${formatUtcTime(trace.timestamps.t7_silver_merged)}</div>
          <div><span style="color: var(--text-muted);">t8 Gold Refreshed:</span> ${formatUtcTime(trace.timestamps.t8_gold_refreshed)}</div>
          <div><span style="color: var(--text-muted);">t9 Serving Ready:</span> ${formatUtcTime(trace.timestamps.t9_serving_ready)}</div>
        </div>
      </div>

      <div class="card">
        <div style="font-size: 0.75rem; font-weight: 700; margin-bottom: 8px;">Parallel Branch Latency Decomposition</div>
        <div style="display: flex; flex-direction: column; gap: 4px; font-family: var(--font-mono); font-size: 0.75rem;">
          <div>Spine: ${formatLatency(trace.latencies.serial_spine_ms)}</div>
          <div>Hot Branch: ${formatLatency(trace.latencies.hot_branch_ms)}</div>
          <div>OLAP Branch: ${formatLatency(trace.latencies.olap_branch_ms)}</div>
          <div>Lakehouse Branch: ${formatLatency(trace.latencies.lakehouse_branch_ms)}</div>
          <div style="font-weight: 700; color: #10b981; border-top: 1px solid var(--border-subtle); padding-top: 4px;">
            Critical Serving Path: ${formatLatency(trace.latencies.end_to_end_serving_ms)}
          </div>
        </div>
      </div>
    `;

    this.activeDrawer.setContent(content);
    this.activeDrawer.open();
  }

  private getNodeDescription(id: string): string {
    switch (id) {
      case 'collector_ws':
        return 'Provider-isolated asynchronous WebSocket collector connecting to Binance Spot with automatic reconnection, heartbeats, and Token Bucket rate-limiting.';
      case 'kafka_cluster':
        return 'Apache Kafka KRaft partitioned by {provider}:{symbol}. Guarantees partition-ordered delivery and DLQ isolation.';
      case 'redis_hot':
        return 'In-memory hot state projection using atomic Lua monotonic timestamp checks. Guarantees sub-15ms quotes without race conditions.';
      case 'clickhouse_olap':
        return 'High-performance analytical datastore utilizing ReplacingMergeTree tables with deterministic UUIDv5 natural keys.';
      case 'minio_bronze':
        return 'S3-compatible immutable object storage recording exact raw Kafka envelopes in partitioned Parquet files.';
      case 'silver_iceberg':
        return 'PySpark-standardized and deduplicated tables registered in Apache Iceberg v2 catalog format.';
      case 'gold_marts':
        return 'dbt Core curated business and quantitative marts computing multi-timeframe OHLCV rollups and volatility.';
      case 'fastapi_serving':
        return 'FastAPI modular monolith and domain microservices enforcing Clean Architecture boundaries and Selective CQRS.';
      default:
        return 'Core platform component participating in the 12-stage financial data lifecycle.';
    }
  }
}

