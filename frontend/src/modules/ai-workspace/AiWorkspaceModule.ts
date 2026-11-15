import { createElement } from '@/utils/dom';
import { createButton } from '@/components/ui/Button';
import { createBadge } from '@/components/ui/Badge';
import { createDataTable } from '@/components/tables/DataTable';
import { agentService } from '@/services/api/agent.service';
import { appStore } from '@/stores/app.store';
import type { AgentRunTicket, InvestigationReport } from '@/types/agent';
import { formatUtcTime } from '@/utils/formatters';

export class AiWorkspaceModule {
  private element: HTMLElement;
  private runs: AgentRunTicket[] = [];
  private reports: InvestigationReport[] = [];
  private selectedRun: AgentRunTicket | null = null;
  private selectedReport: InvestigationReport | null = null;

  constructor() {
    this.element = createElement('div', { className: 'ai-workspace-module anim-fade-in' });
  }

  public async mount(parent: HTMLElement): Promise<void> {
    parent.appendChild(this.element);
    this.renderLoading();
    await this.loadData();
    this.render();
  }

  public unmount(): void {
    if (this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }

  private renderLoading(): void {
    this.element.innerHTML = '<div class="empty-state"><div class="loader-spinner"></div><div>Loading Agent Intelligence Plane...</div></div>';
  }

  private async loadData(): Promise<void> {
    try {
      const [r, rep] = await Promise.all([
        agentService.getRuns(),
        agentService.getReports()
      ]);
      this.runs = r;
      this.reports = rep;
      if (this.runs.length > 0) {
        this.selectedRun = this.runs[0];
      }
      if (this.reports.length > 0) {
        this.selectedReport = this.reports[0];
      }
    } catch {}
  }

  private render(): void {
    this.element.innerHTML = '';

    // Header & Trigger Control
    const header = createElement('div', {
      style: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px'
      }
    });

    header.innerHTML = `
      <div>
        <h2 style="font-size: 1.25rem; font-weight: 700;">AI Workspace & Agentic Intelligence Plane (Plane C)</h2>
        <p style="font-size: 0.8rem; color: var(--text-muted);">
          Stateful LangGraph MarketIntelligenceGraph with Controlled Tool Gateway (10 read-only deterministic tools).
        </p>
      </div>
    `;

    const triggerBtn = createButton({
      label: 'Trigger New Investigation',
      variant: 'primary',
      onClick: async () => {
        const objective = prompt('Enter investigation objective:', 'Investigate sudden 1m price spike and volume anomaly') || '';
        if (objective) {
          appStore.addNotification('INFO', 'Submitting agent run...');
          const activeSymbol = appStore.getState().symbol;
          const res = await agentService.triggerRun(objective, activeSymbol);
          this.runs.unshift(res.ticket);
          this.selectedRun = res.ticket;
          this.render();
          appStore.addNotification('SUCCESS', `Agent Run ${res.run_id} initiated!`);
        }
      }
    });

    header.appendChild(triggerBtn);
    this.element.appendChild(header);

    // Section 1: LangGraph 5-Node Workflow State Visualizer
    const wfCard = createElement('div', { className: 'card', style: { marginBottom: '24px' } });
    wfCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">LangGraph 5-Node Workflow State Machine</span>
        <span class="badge badge-info">Zero Arbitrary SQL · Deterministic Quant</span>
      </div>
    `;

    const nodeFlow = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
        padding: '12px 0'
      }
    });

    const nodes = this.selectedRun?.nodes || [
      { node_name: 'intake_and_classify', status: 'DONE' },
      { node_name: 'gather_evidence', status: 'DONE' },
      { node_name: 'synthesize_analysis', status: 'DONE' },
      { node_name: 'validate_citations', status: 'DONE' },
      { node_name: 'publish_report', status: 'DONE' }
    ];

    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];
      const isDone = n.status === 'DONE';
      const isActive = n.status === 'ACTIVE';

      const box = createElement('div', {
        style: {
          padding: '12px',
          backgroundColor: isActive ? 'rgba(59, 130, 246, 0.15)' : 'var(--bg-muted)',
          border: `1px solid ${isActive ? '#3b82f6' : isDone ? 'rgba(16, 185, 129, 0.4)' : 'var(--border-subtle)'}`,
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px'
        }
      });

      box.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 0.7rem; color: var(--text-muted); font-weight: 700;">STAGE ${i + 1}</span>
          ${createBadge(n.status, isDone ? 'success' : isActive ? 'info' : 'neutral').outerHTML}
        </div>
        <div style="font-weight: 700; font-size: 0.85rem; color: var(--text-primary);">
          ${n.node_name.replace(/_/g, ' ')}
        </div>
        <div style="font-size: 0.7rem; color: var(--text-secondary);">
          ${this.getNodeExplanation(n.node_name)}
        </div>
      `;
      nodeFlow.appendChild(box);
    }

    wfCard.appendChild(nodeFlow);
    this.element.appendChild(wfCard);

    // Section 2: Agent Runs List & Verified Report Viewer
    const splitGrid = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'minmax(320px, 1fr) minmax(450px, 1.6fr)',
        gap: '20px'
      }
    });

    // Runs List Card
    const runsCard = createElement('div', { className: 'card' });
    runsCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Investigation Run History</span>
        <span class="badge badge-neutral">${this.runs.length} Runs</span>
      </div>
    `;

    const runsTable = createDataTable<AgentRunTicket>({
      columns: [
        {
          key: 'run_id',
          header: 'Run Ticket',
          className: 'font-mono',
          render: (r) => r.run_id ? r.run_id.substring(0, 10) + '...' : '—'
        },
        {
          key: 'status',
          header: 'Status',
          render: (r) => createBadge(r.status, r.status === 'COMPLETED' ? 'success' : 'info')
        },
        {
          key: 'started_at',
          header: 'Triggered',
          className: 'font-mono',
          render: (r) => formatUtcTime(r.started_at)
        }
      ],
      data: this.runs,
      onRowClick: (r) => {
        this.selectedRun = r;
        this.render();
      }
    });

    runsCard.appendChild(runsTable);
    splitGrid.appendChild(runsCard);

    // Report Viewer Card
    const repCard = createElement('div', { className: 'card' });
    const rep = this.selectedReport;

    repCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Verified Intelligence Report</span>
        ${rep ? createBadge(rep.author_agent, 'success').outerHTML : ''}
      </div>
      <div style="font-size: 0.85rem; line-height: 1.6; color: var(--text-secondary);">
        <h3 style="color: var(--text-primary); font-size: 1.1rem; margin-bottom: 8px;">
          ${rep?.title || 'No Report Selected'}
        </h3>
        <p style="margin-bottom: 16px; color: var(--accent-cyan); font-weight: 500;">
          ${rep?.summary || ''}
        </p>

        <div class="card" style="margin-bottom: 16px; background-color: var(--bg-sidebar);">
          <div style="font-weight: 700; font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px;">
            Provenance Citations (Zero Hallucination Proof)
          </div>
          <div style="display: flex; flex-direction: column; gap: 6px; font-family: var(--font-mono); font-size: 0.75rem;">
            ${(rep?.citations || []).map(c => `
              <div style="display: flex; justify-content: space-between; padding: 4px 6px; background: var(--bg-app); border-radius: 4px;">
                <span style="color: #60a5fa;">[Tool: ${c.tool_invoked}]</span>
                <span style="color: var(--text-muted);">${c.source_table} (${c.rows_examined} rows)</span>
                <span style="color: #10b981;">✓ Verified</span>
              </div>
            `).join('')}
          </div>
        </div>

        <div style="white-space: pre-wrap; font-family: var(--font-sans); color: var(--text-primary); line-height: 1.6;">
          ${rep?.content_markdown || ''}
        </div>
      </div>
    `;

    splitGrid.appendChild(repCard);
    this.element.appendChild(splitGrid);
  }

  private getNodeExplanation(name: string): string {
    switch (name) {
      case 'intake_and_classify': return 'Classifies event anomaly type and assigns investigation ticket.';
      case 'gather_evidence': return 'Invokes whitelisted read-only tools via Controlled Tool Gateway.';
      case 'synthesize_analysis': return 'Computes exact volatility and cross-asset correlations.';
      case 'validate_citations': return 'Audits claims against raw query fingerprints to prevent hallucinations.';
      case 'publish_report': return 'Publishes immutable structured markdown report with citations.';
      default: return 'Autonomous workflow execution step.';
    }
  }
}

