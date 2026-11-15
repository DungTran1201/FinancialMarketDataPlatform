import { createElement } from '@/utils/dom';
import { appStore } from '@/stores/app.store';
import type { RoutePath } from '@/types/navigation';
import type { SymbolKey } from '@/types/market';
import { sseClient } from '@/services/api/sse';
import { wsClient } from '@/services/websocket/ws-client';

export interface NavItemConfig {
  id: string;
  label: string;
  path: RoutePath;
  iconSvg: string;
}

export class MainLayout {
  private element: HTMLElement;
  private contentViewport: HTMLElement;
  private currentPath: RoutePath = '/dashboard';
  private connectionBadge!: HTMLElement;
  private clockElement!: HTMLElement;
  private clockInterval: any = null;

  private navItems: NavItemConfig[] = [
    {
      id: 'dashboard',
      label: 'Overview Dashboard',
      path: '/dashboard',
      iconSvg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
    },
    {
      id: 'data-flow',
      label: 'Data Flow Observatory',
      path: '/data-flow',
      iconSvg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    },
    {
      id: 'market-analytics',
      label: 'Market Analytics',
      path: '/market-analytics',
      iconSvg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>'
    },
    {
      id: 'data-management',
      label: 'Data Management',
      path: '/data-management',
      iconSvg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>'
    },
    {
      id: 'ai-workspace',
      label: 'AI Workspace',
      path: '/ai-workspace',
      iconSvg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10H12V2z"/><circle cx="12" cy="12" r="3"/></svg>'
    },
    {
      id: 'administration',
      label: 'Administration',
      path: '/administration',
      iconSvg: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    }
  ];

  constructor() {
    this.element = createElement('div', { className: 'app-shell' });
    this.contentViewport = createElement('div', {
      id: 'app-content-viewport',
      className: 'app-content'
    });

    this.buildLayout();
    this.bindConnectionListeners();
    this.startClock();
  }

  public getElement(): HTMLElement {
    return this.element;
  }

  public getContentViewport(): HTMLElement {
    return this.contentViewport;
  }

  public setRoute(path: RoutePath): void {
    this.currentPath = path;
    const links = this.element.querySelectorAll<HTMLAnchorElement>('.nav-link');
    for (const l of links) {
      if (l.getAttribute('href') === `#${path}`) {
        l.classList.add('active');
      } else {
        l.classList.remove('active');
      }
    }
  }

  private buildLayout(): void {
    this.element.innerHTML = '';

    // 1. Sidebar
    const sidebar = createElement('aside', { className: 'app-sidebar' });
    sidebar.innerHTML = `
      <div class="sidebar-header">
        <a href="#/dashboard" class="brand-wrapper">
          <svg class="brand-logo" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="6" fill="#0A0E17"/>
            <path d="M4 22L11 14L17 19L28 8" stroke="#3B82F6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="28" cy="8" r="3" fill="#10B981"/>
          </svg>
          <span class="brand-title">FMDP Platform</span>
          <span class="brand-badge">EXP</span>
        </a>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Experience Layer</div>
        ${this.navItems.map(item => `
          <a href="#${item.path}" class="nav-link ${item.path === this.currentPath ? 'active' : ''}">
            <span class="nav-icon">${item.iconSvg}</span>
            <span class="nav-label">${item.label}</span>
          </a>
        `).join('')}
      </nav>
      <div class="sidebar-footer">
        <div class="version-info">
          <span>Platform v0.1.0</span>
          <span style="color: #10b981;">Online</span>
        </div>
      </div>
    `;

    // 2. Main Area (Header + Viewport + Status Bar)
    const main = createElement('div', { className: 'app-main' });

    // Header
    const header = createElement('header', { className: 'app-header' });
    header.innerHTML = `
      <div class="header-left">
        <span class="page-title">Financial Market Data Platform</span>
      </div>
      <div class="header-right">
        <!-- Live vs Demo Mode Toggle -->
        <div class="mode-toggle">
          <button id="btn-mode-live" class="mode-btn ${appStore.getState().mode === 'LIVE' ? 'active' : ''}">LIVE</button>
          <button id="btn-mode-demo" class="mode-btn ${appStore.getState().mode === 'DEMO' ? 'active' : ''}">DEMO</button>
        </div>

        <!-- Symbol Selector -->
        <select id="select-symbol" class="symbol-picker">
          <option value="BTCUSDT" ${appStore.getState().symbol === 'BTCUSDT' ? 'selected' : ''}>BTC/USDT</option>
          <option value="ETHUSDT" ${appStore.getState().symbol === 'ETHUSDT' ? 'selected' : ''}>ETH/USDT</option>
          <option value="SOLUSDT" ${appStore.getState().symbol === 'SOLUSDT' ? 'selected' : ''}>SOL/USDT</option>
          <option value="BNBUSDT" ${appStore.getState().symbol === 'BNBUSDT' ? 'selected' : ''}>BNB/USDT</option>
          <option value="ADAUSDT" ${appStore.getState().symbol === 'ADAUSDT' ? 'selected' : ''}>ADA/USDT</option>
        </select>

        <!-- SSE/WS Status Badge -->
        <div id="conn-badge" class="connection-badge">
          <span class="status-dot connected"></span>
          <span id="conn-text">SSE Stream</span>
        </div>
      </div>
    `;

    // Bind Header Controls
    const btnLive = header.querySelector('#btn-mode-live') as HTMLButtonElement;
    const btnDemo = header.querySelector('#btn-mode-demo') as HTMLButtonElement;
    const selSymbol = header.querySelector('#select-symbol') as HTMLSelectElement;
    this.connectionBadge = header.querySelector('#conn-badge') as HTMLElement;

    btnLive.addEventListener('click', () => {
      appStore.setMode('LIVE');
      btnLive.classList.add('active');
      btnDemo.classList.remove('active');
    });

    btnDemo.addEventListener('click', () => {
      appStore.setMode('DEMO');
      btnDemo.classList.add('active');
      btnLive.classList.remove('active');
    });

    selSymbol.addEventListener('change', () => {
      appStore.setSymbol(selSymbol.value as SymbolKey);
    });

    main.appendChild(header);
    main.appendChild(this.contentViewport);

    // Status Bar (Footer)
    const statusBar = createElement('footer', { className: 'app-status-bar' });
    statusBar.innerHTML = `
      <div class="status-bar-group">
        <span class="status-metric"><span>Plane A:</span> <span class="metric-highlight">Kafka + ClickHouse + Redis</span></span>
        <span class="status-metric"><span>Plane B:</span> <span class="metric-highlight">FastAPI Monolith (8 Contexts)</span></span>
        <span class="status-metric"><span>Plane C:</span> <span class="metric-highlight">LangGraph Agent Plane</span></span>
      </div>
      <div class="status-bar-group">
        <span class="status-metric"><span>Defense:</span> <span class="metric-highlight">WAF + AES-GCM</span></span>
        <span id="clock-display" class="status-metric font-mono">--:--:-- UTC</span>
      </div>
    `;
    this.clockElement = statusBar.querySelector('#clock-display') as HTMLElement;
    main.appendChild(statusBar);

    this.element.appendChild(sidebar);
    this.element.appendChild(main);
  }

  private bindConnectionListeners(): void {
    sseClient.on('connection', (e: any) => {
      if (e.status === 'CONNECTED') {
        this.connectionBadge.innerHTML = '<span class="status-dot connected"></span><span>SSE Live</span>';
        appStore.setConnection('CONNECTED');
      } else {
        this.connectionBadge.innerHTML = '<span class="status-dot disconnected"></span><span>Disconnected</span>';
        appStore.setConnection('DISCONNECTED');
      }
    });

    wsClient.onConnectionChange((connected) => {
      if (connected) {
        appStore.setConnection('CONNECTED');
      }
    });
  }

  private startClock(): void {
    if (this.clockInterval) clearInterval(this.clockInterval);
    const update = () => {
      if (this.clockElement) {
        const d = new Date();
        this.clockElement.textContent = d.toISOString().substring(11, 19) + ' UTC';
      }
    };
    update();
    this.clockInterval = setInterval(update, 1000);
  }
}
