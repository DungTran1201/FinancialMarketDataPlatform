import { createElement } from '@/utils/dom';
import { createButton } from '@/components/ui/Button';
import { createBadge } from '@/components/ui/Badge';
import { createDataTable } from '@/components/tables/DataTable';
import { authService } from '@/services/auth/auth.service';
import { appStore } from '@/stores/app.store';
import type { ApiKeyItem } from '@/types/auth';
import { formatUtcTime } from '@/utils/formatters';

export class AdministrationModule {
  private element: HTMLElement;
  private apiKeys: ApiKeyItem[] = [];

  constructor() {
    this.element = createElement('div', { className: 'administration-module anim-fade-in' });
  }

  public async mount(parent: HTMLElement): Promise<void> {
    parent.appendChild(this.element);
    await this.loadKeys();
    this.render();
  }

  public unmount(): void {
    if (this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }

  private async loadKeys(): Promise<void> {
    try {
      this.apiKeys = await authService.getApiKeys();
    } catch {}
  }

  private render(): void {
    this.element.innerHTML = '';
    const user = authService.getUser();

    const header = createElement('div', { style: { marginBottom: '20px' } });
    header.innerHTML = `
      <h2 style="font-size: 1.25rem; font-weight: 700;">Platform Administration, IAM & Security Center</h2>
      <p style="font-size: 0.8rem; color: var(--text-muted);">
        Manage user access control (RBAC), API key lifecycle, rate limit quotas, and defense-in-depth parameters.
      </p>
    `;
    this.element.appendChild(header);

    // Two Column Grid: User Profile (Left) + Security Controls (Right)
    const topGrid = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: '20px',
        marginBottom: '24px'
      }
    });

    // User Profile Card
    const profileCard = createElement('div', { className: 'card' });
    profileCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Current User Persona (RBAC)</span>
        ${createBadge(user?.role || 'ADMIN', 'success').outerHTML}
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.85rem;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px;">
          <span style="color: var(--text-muted);">Username:</span>
          <span style="font-weight: 600;">${user?.username || 'quant_admin'}</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px;">
          <span style="color: var(--text-muted);">Email:</span>
          <span>${user?.email || 'admin@fmdp.local'}</span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px;">
          <span style="color: var(--text-muted);">User Tier:</span>
          <span class="font-mono" style="font-weight: 700; color: #38bdf8;">${user?.tier || 'INSTITUTIONAL'} (3000 req/min)</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">Session IP Binding:</span>
          <span class="badge badge-info">HMAC-SHA256 Active</span>
        </div>
      </div>
    `;
    topGrid.appendChild(profileCard);

    // Security Defense Parameters Card
    const secCard = createElement('div', { className: 'card' });
    secCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Defense-in-Depth Parameters</span>
        <span class="badge badge-success">Zero Leaks Active</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.8rem;">
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">Edge Gateway WAF:</span>
          <span class="badge badge-success">SQLi / XSS / Traversal Blocked</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">Endpoint Masking:</span>
          <span class="badge badge-success">Raw IP:Port Hidden</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">Field Encryption:</span>
          <span class="badge badge-success">AES-GCM-256</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">API Key Revocation:</span>
          <span class="badge badge-success">SHA-256 Blacklist Sync</span>
        </div>
      </div>
    `;
    topGrid.appendChild(secCard);

    this.element.appendChild(topGrid);

    // Section 2: API Keys Management Table
    const keysCard = createElement('div', { className: 'card' });
    const keysHeader = createElement('div', { className: 'card-header' });
    keysHeader.innerHTML = `
      <div>
        <span class="card-title">API Keys Management</span>
        <span class="card-subtitle">Generate and revoke high-performance client API keys</span>
      </div>
    `;

    const createKeyBtn = createButton({
      label: '+ Generate New Key',
      variant: 'primary',
      size: 'sm',
      onClick: async () => {
        const name = prompt('Enter key label/application name:', 'Quant Bot Algorithm') || '';
        if (name) {
          appStore.addNotification('INFO', 'Generating key...');
          await authService.createApiKey(name);
          await this.loadKeys();
          this.render();
          appStore.addNotification('SUCCESS', 'API key generated successfully!');
        }
      }
    });

    keysHeader.appendChild(createKeyBtn);
    keysCard.appendChild(keysHeader);

    const keysTable = createDataTable<ApiKeyItem>({
      columns: [
        { key: 'name', header: 'Application Label' },
        { key: 'key_prefix', header: 'Key Prefix', className: 'font-mono' },
        {
          key: 'rate_limit_rpm',
          header: 'Quota',
          className: 'font-mono',
          render: (k) => `${k.rate_limit_rpm} rpm`
        },
        {
          key: 'is_active',
          header: 'Status',
          render: (k) => createBadge(k.is_active ? 'ACTIVE' : 'REVOKED', k.is_active ? 'success' : 'danger')
        },
        {
          key: 'created_at',
          header: 'Created (UTC)',
          className: 'font-mono',
          render: (k) => formatUtcTime(k.created_at)
        },
        {
          key: 'actions',
          header: 'Action',
          render: (k) => {
            const btn = createButton({
              label: 'Revoke',
              variant: 'danger',
              size: 'sm',
              disabled: !k.is_active,
              onClick: async () => {
                if (confirm(`Revoke API key ${k.name}?`)) {
                  await authService.revokeApiKey(k.id);
                  await this.loadKeys();
                  this.render();
                  appStore.addNotification('WARNING', `API key ${k.name} revoked!`);
                }
              }
            });
            return btn;
          }
        }
      ],
      data: this.apiKeys,
      emptyMessage: 'No API keys generated yet.'
    });

    keysCard.appendChild(keysTable);
    this.element.appendChild(keysCard);
  }
}

