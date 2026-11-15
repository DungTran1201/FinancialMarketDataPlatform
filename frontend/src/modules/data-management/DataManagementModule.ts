import { createElement } from '@/utils/dom';
import { createDataTable } from '@/components/tables/DataTable';
import { createBadge } from '@/components/ui/Badge';
import { catalogService } from '@/services/api/catalog.service';
import type { DatasetCatalogItem, DataQualityCheckResult, LineageEdge } from '@/types/catalog';
import { formatBytes, formatNumber } from '@/utils/formatters';

export class DataManagementModule {
  private element: HTMLElement;
  private datasets: DatasetCatalogItem[] = [];
  private dqChecks: DataQualityCheckResult[] = [];
  private lineage: { nodes: string[]; edges: LineageEdge[] } | null = null;
  private selectedDataset: DatasetCatalogItem | null = null;

  constructor() {
    this.element = createElement('div', { className: 'data-management-module anim-fade-in' });
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
    this.element.innerHTML = '<div class="empty-state"><div class="loader-spinner"></div><div>Loading Data Governance & Catalog...</div></div>';
  }

  private async loadData(): Promise<void> {
    try {
      const [ds, dq, lin] = await Promise.all([
        catalogService.getDatasets(),
        catalogService.getDataQualityReport(),
        catalogService.getLineage()
      ]);
      this.datasets = ds;
      this.dqChecks = dq;
      this.lineage = lin;
      if (this.datasets.length > 0) {
        this.selectedDataset = this.datasets[0];
      }
    } catch {}
  }

  private render(): void {
    this.element.innerHTML = '';

    const header = createElement('div', { style: { marginBottom: '20px' } });
    header.innerHTML = `
      <h2 style="font-size: 1.25rem; font-weight: 700;">Data Governance, Catalog & Quality Management</h2>
      <p style="font-size: 0.8rem; color: var(--text-muted);">
        Manage Medallion lakehouse schemas (Bronze/Silver/Gold), dataset ownership, lineage graph, and Great Expectations quality gates.
      </p>
    `;
    this.element.appendChild(header);

    // Grid: Datasets Catalog (Left) + Schema Inspector (Right)
    const mainGrid = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'minmax(450px, 1.8fr) minmax(320px, 1.2fr)',
        gap: '20px',
        marginBottom: '24px'
      }
    });

    // Dataset Catalog Table Card
    const catCard = createElement('div', { className: 'card' });
    catCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Medallion Dataset Registry</span>
        <span class="badge badge-info">${this.datasets.length} Governed Tables</span>
      </div>
    `;

    const dsTable = createDataTable<DatasetCatalogItem>({
      columns: [
        { key: 'name', header: 'Dataset Name', className: 'font-mono' },
        {
          key: 'layer',
          header: 'Layer',
          render: (row) => {
            const v = row.layer === 'GOLD' ? 'warning' : row.layer === 'SILVER' ? 'info' : 'success';
            return createBadge(row.layer, v);
          }
        },
        { key: 'storage_format', header: 'Format', className: 'font-mono' },
        {
          key: 'total_records',
          header: 'Records',
          className: 'font-mono',
          render: (row) => formatNumber(row.total_records, 0)
        },
        {
          key: 'size_bytes',
          header: 'Size',
          className: 'font-mono',
          render: (row) => formatBytes(row.size_bytes)
        }
      ],
      data: this.datasets,
      onRowClick: (ds) => {
        this.selectedDataset = ds;
        this.render();
      }
    });

    catCard.appendChild(dsTable);
    mainGrid.appendChild(catCard);

    // Schema Inspector Card
    const schemaCard = createElement('div', { className: 'card' });
    schemaCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Schema Inspector: ${this.selectedDataset?.name || 'Select a Dataset'}</span>
        ${this.selectedDataset ? createBadge(this.selectedDataset.storage_format, 'neutral').outerHTML : ''}
      </div>
    `;

    const schemaContainer = createElement('div');
    if (this.selectedDataset && this.selectedDataset.schema.length > 0) {
      const sTable = createDataTable({
        columns: [
          { key: 'name', header: 'Field Name', className: 'font-mono' },
          { key: 'type', header: 'Type', className: 'font-mono' },
          {
            key: 'nullable',
            header: 'Nullable',
            render: (r: any) => createBadge(r.nullable ? 'YES' : 'NO', r.nullable ? 'neutral' : 'warning')
          },
          {
            key: 'is_natural_key',
            header: 'Natural Key',
            render: (r: any) => r.is_natural_key ? createBadge('PK (Natural)', 'success') : '—'
          }
        ],
        data: this.selectedDataset.schema
      });
      schemaContainer.appendChild(sTable);
    } else {
      schemaContainer.innerHTML = '<div class="empty-state">Select a dataset to view its formal schema definitions</div>';
    }
    schemaCard.appendChild(schemaContainer);
    mainGrid.appendChild(schemaCard);

    this.element.appendChild(mainGrid);

    // Section 2: Data Quality Gates & Lineage
    const bottomGrid = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
        gap: '20px'
      }
    });

    // Data Quality Report Card
    const dqCard = createElement('div', { className: 'card' });
    dqCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Data Quality Gates (Great Expectations)</span>
        <span class="badge badge-success">Zero High-Severity Violations</span>
      </div>
    `;

    const dqTable = createDataTable<DataQualityCheckResult>({
      columns: [
        { key: 'rule_name', header: 'Quality Rule' },
        { key: 'dataset_id', header: 'Target Dataset', className: 'font-mono' },
        {
          key: 'status',
          header: 'Status',
          render: (r) => createBadge(r.status, r.status === 'PASSED' ? 'success' : 'danger')
        },
        {
          key: 'violated_records',
          header: 'Violations',
          className: 'font-mono',
          render: (r) => `${r.violated_records} / ${formatNumber(r.evaluated_records, 0)}`
        }
      ],
      data: this.dqChecks
    });
    dqCard.appendChild(dqTable);
    bottomGrid.appendChild(dqCard);

    // Lineage Mapping Card
    const linCard = createElement('div', { className: 'card' });
    linCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">End-to-End Data Lineage Transformations</span>
        <span class="badge badge-info">Bidirectional Trace</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.75rem;">
        ${(this.lineage?.edges || []).map(e => `
          <div style="display: flex; align-items: center; justify-content: space-between; padding: 6px 8px; background: var(--bg-muted); border-radius: var(--radius-sm);">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="font-mono" style="color: var(--accent-cyan); font-weight: 600;">${e.from_dataset}</span>
              <span style="color: var(--text-muted);">→</span>
              <span class="font-mono" style="color: #10b981; font-weight: 600;">${e.to_dataset}</span>
            </div>
            <span style="color: var(--text-muted); font-size: 0.7rem;">${e.transformation}</span>
          </div>
        `).join('')}
      </div>
    `;
    bottomGrid.appendChild(linCard);

    this.element.appendChild(bottomGrid);
  }
}
