import type { ParallelBranchLatency } from '@/types/observability';
import { createElement } from '@/utils/dom';
import { formatLatency } from '@/utils/formatters';

export class LatencyHistogram {
  private container: HTMLElement;

  constructor(container: HTMLElement) {
    this.container = container;
  }

  public setData(latencies: ParallelBranchLatency | null): void {
    this.container.innerHTML = '';

    if (!latencies) {
      this.container.innerHTML = '<div class="empty-state">No latency data</div>';
      return;
    }

    const card = createElement('div', { className: 'card' });
    const header = createElement('div', { className: 'card-header' });
    header.innerHTML = '<div class="card-title">Parallel-Branch Latency Breakdown (Non-Summed Critical Path)</div>';
    card.appendChild(header);

    const branches = [
      { name: '1. Serial Spine (Ingest + Kafka Broker)', ms: latencies.serial_spine_ms, color: '#38bdf8' },
      { name: '2. Hot Branch (Redis Monotonic Lua)', ms: latencies.hot_branch_ms, color: '#f87171' },
      { name: '3. OLAP Branch (ClickHouse Ingest)', ms: latencies.olap_branch_ms, color: '#fbbf24' },
      { name: '4. Lakehouse Branch (Bronze + Silver + Gold)', ms: latencies.lakehouse_branch_ms, color: '#34d399' },
      { name: 'Serving Hot End-to-End (Spine + Hot)', ms: latencies.serving_hot_e2e_ms, color: '#60a5fa' },
      { name: 'Serving OLAP End-to-End (Spine + OLAP)', ms: latencies.serving_olap_e2e_ms, color: '#f59e0b' },
      { name: 'Critical Serving E2E (Max Parallel Branch)', ms: latencies.end_to_end_serving_ms, color: '#10b981', isTotal: true }
    ];

    const maxMs = Math.max(...branches.map(b => b.ms), 10);

    const list = createElement('div', {
      style: { display: 'flex', flexDirection: 'column', gap: '10px' }
    });

    for (const b of branches) {
      const row = createElement('div', {
        style: {
          display: 'flex',
          flexDirection: 'column',
          gap: '4px',
          padding: b.isTotal ? '8px' : '4px 0',
          borderTop: b.isTotal ? '1px solid var(--border-default)' : 'none',
          backgroundColor: b.isTotal ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
          borderRadius: b.isTotal ? 'var(--radius-sm)' : '0'
        }
      });

      const labelRow = createElement('div', {
        style: { display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }
      });
      labelRow.innerHTML = `
        <span style="${b.isTotal ? 'font-weight: 700; color: #10b981;' : 'color: var(--text-secondary);'}">${b.name}</span>
        <span class="font-mono" style="font-weight: 600; color: var(--text-primary);">${formatLatency(b.ms)}</span>
      `;

      const barBg = createElement('div', {
        style: {
          width: '100%',
          height: b.isTotal ? '10px' : '6px',
          backgroundColor: 'var(--bg-muted)',
          borderRadius: 'var(--radius-full)',
          overflow: 'hidden'
        }
      });

      const pct = Math.min(100, Math.max(2, (b.ms / maxMs) * 100));
      const barFill = createElement('div', {
        style: {
          width: `${pct}%`,
          height: '100%',
          backgroundColor: b.color,
          borderRadius: 'var(--radius-full)',
          transition: 'width 0.3s ease'
        }
      });

      barBg.appendChild(barFill);
      row.appendChild(labelRow);
      row.appendChild(barBg);
      list.appendChild(row);
    }

    card.appendChild(list);
    this.container.appendChild(card);
  }
}

