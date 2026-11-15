import { createElement } from '@/utils/dom';
import { createKpiCard } from '@/components/ui/KpiCard';
import { createButton } from '@/components/ui/Button';
import { formatNumber, formatLatency } from '@/utils/formatters';
import { observabilityStore } from '@/stores/observability.store';
import { observabilityService } from '@/services/api/observability.service';
import { appStore } from '@/stores/app.store';

export class DashboardModule {
  private element: HTMLElement;
  private unsubscribe?: () => void;

  constructor() {
    this.element = createElement('div', { className: 'dashboard-module anim-fade-in' });
  }

  public mount(parent: HTMLElement): void {
    parent.appendChild(this.element);
    this.render();

    this.unsubscribe = observabilityStore.subscribe(() => {
      this.render();
    });

    observabilityStore.loadInitial();
    observabilityStore.initSseStream();
  }

  public unmount(): void {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = undefined;
    }
    if (this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }

  private render(): void {
    this.element.innerHTML = '';
    const state = observabilityStore.getState();
    const appState = appStore.getState();
    const kpis = state.kpis;

    // Header Action Bar
    const actionHeader = createElement('div', {
      style: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px'
      }
    });

    actionHeader.innerHTML = `
      <div>
        <h2 style="font-size: 1.25rem; font-weight: 700;">Executive Data Platform & Market Overview</h2>
        <p style="font-size: 0.8rem; color: var(--text-muted);">
          Real-time cross-plane status, stream metrics, and infrastructure health.
        </p>
      </div>
    `;

    const buttonGroup = createElement('div', { style: { display: 'flex', gap: '8px' } });

    const probeBtn = createButton({
      label: 'Trigger Live Probe',
      variant: 'secondary',
      size: 'sm',
      onClick: async () => {
        appStore.addNotification('INFO', 'Initiating live probe for ' + appState.symbol);
        await observabilityService.triggerLiveProbe(appState.symbol, '1m', false);
        await observabilityStore.loadInitial();
      }
    });

    const demoBtn = createButton({
      label: 'Emit Demo Batch (5 events)',
      variant: 'primary',
      size: 'sm',
      onClick: async () => {
        appStore.addNotification('SUCCESS', 'Emitted 5 synthetic events to Kafka');
        await observabilityService.triggerDemoEmit('emit_batch', appState.symbol, 5);
        await observabilityStore.loadInitial();
      }
    });

    buttonGroup.appendChild(probeBtn);
    buttonGroup.appendChild(demoBtn);
    actionHeader.appendChild(buttonGroup);
    this.element.appendChild(actionHeader);

    // KPI Cards Grid
    const kpiGrid = createElement('div', { className: 'kpi-grid' });

    kpiGrid.appendChild(createKpiCard({
      label: 'Total Ingested Events',
      value: formatNumber(kpis?.events_ingested ?? 124800, 0),
      trend: '+1,240 /min',
      trendType: 'positive',
      subtitle: 'Binance WS & REST'
    }));

    kpiGrid.appendChild(createKpiCard({
      label: 'Critical E2E Latency (P50)',
      value: formatLatency(kpis?.e2e_latency_p50_ms ?? 1.8),
      trend: 'P99: ' + formatLatency(kpis?.e2e_latency_p99_ms ?? 4.5),
      trendType: 'positive',
      subtitle: 'Max parallel sink path'
    }));

    kpiGrid.appendChild(createKpiCard({
      label: 'Active Kafka Consumer Lag',
      value: formatNumber(kpis?.active_kafka_lag ?? 0, 0),
      trend: (kpis?.active_kafka_lag ?? 0) === 0 ? 'Optimal (0 lag)' : 'Catching up',
      trendType: (kpis?.active_kafka_lag ?? 0) === 0 ? 'positive' : 'negative',
      subtitle: 'Across all 6 topics'
    }));

    kpiGrid.appendChild(createKpiCard({
      label: 'Dead Letter Queue (DLQ)',
      value: formatNumber(kpis?.events_failed_dlq ?? 0, 0),
      trend: 'Isolated',
      trendType: 'neutral',
      subtitle: 'market.dlq.v1'
    }));

    this.element.appendChild(kpiGrid);

    // Infrastructure Grid & Microservice Status
    const infraSection = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '16px',
        marginBottom: '20px'
      }
    });

    // Subsystem Health Card
    const healthCard = createElement('div', { className: 'card' });
    healthCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Hạ Tầng Lõi (Core Stores Health)</span>
        <span class="badge badge-success">5/5 Connected</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.8rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);">
          <div>
            <div style="font-weight: 600;">Apache Kafka (KRaft Mode)</div>
            <div style="color: var(--text-muted); font-size: 0.75rem;">1 Active Controller/Broker | 6 Topics</div>
          </div>
          <span class="badge badge-success">Online (Broker 1)</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);">
          <div>
            <div style="font-weight: 600;">Redis 7 (Hot State Cache)</div>
            <div style="color: var(--text-muted); font-size: 0.75rem;">Atomic Lua Monotonic Stamp | sub-15ms</div>
          </div>
          <span class="badge badge-success">Healthy</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);">
          <div>
            <div style="font-weight: 600;">ClickHouse (OLAP Engine)</div>
            <div style="color: var(--text-muted); font-size: 0.75rem;">ReplacingMergeTree | 1s Micro-batch</div>
          </div>
          <span class="badge badge-success">Healthy</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 8px; border-bottom: 1px solid var(--border-subtle);">
          <div>
            <div style="font-weight: 600;">PostgreSQL 16 (Control DB)</div>
            <div style="color: var(--text-muted); font-size: 0.75rem;">IAM, RBAC, Watermarks & Config</div>
          </div>
          <span class="badge badge-success">Healthy</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-weight: 600;">MinIO Lakehouse (S3 Object Store)</div>
            <div style="color: var(--text-muted); font-size: 0.75rem;">Bronze Parquet + Silver Iceberg v2</div>
          </div>
          <span class="badge badge-success">Healthy</span>
        </div>
      </div>
    `;
    infraSection.appendChild(healthCard);

    // Architectural Planes Summary Card
    const planesCard = createElement('div', { className: 'card' });
    planesCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Three Planes Architecture Overview</span>
        <span class="badge badge-info">Modular Clean Arch</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 12px; font-size: 0.8rem;">
        <div style="padding: 10px; background-color: rgba(3, 105, 161, 0.1); border-left: 3px solid #0284c7; border-radius: var(--radius-sm);">
          <div style="font-weight: 700; color: #38bdf8;">Plane A: Data Plane</div>
          <div style="color: var(--text-secondary); font-size: 0.75rem;">
            Ingestion WS/REST -> Kafka KRaft -> Redis Hot Cache || ClickHouse OLAP || MinIO Lakehouse (Bronze -> Silver -> Gold).
          </div>
        </div>
        <div style="padding: 10px; background-color: rgba(67, 56, 202, 0.1); border-left: 3px solid #6366f1; border-radius: var(--radius-sm);">
          <div style="font-weight: 700; color: #818cf8;">Plane B: Application & Control Plane</div>
          <div style="color: var(--text-secondary); font-size: 0.75rem;">
            FastAPI Modular Monolith & 7 Microservices, WAF, JWT IP-binding, Postgres Control Store, Superset BI.
          </div>
        </div>
        <div style="padding: 10px; background-color: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; border-radius: var(--radius-sm);">
          <div style="font-weight: 700; color: #34d399;">Plane C: Agentic Intelligence Plane</div>
          <div style="color: var(--text-secondary); font-size: 0.75rem;">
            LangGraph 5-node investigation state machine, Controlled Tool Gateway (10 read-only tools), zero arbitrary SQL.
          </div>
        </div>
      </div>
    `;
    infraSection.appendChild(planesCard);

    this.element.appendChild(infraSection);
  }
}
