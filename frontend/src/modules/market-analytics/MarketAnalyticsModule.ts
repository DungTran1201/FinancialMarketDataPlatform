import { createElement } from '@/utils/dom';
import { CandlestickChart } from '@/components/charts/CandlestickChart';
import { createButton } from '@/components/ui/Button';
import { marketStore } from '@/stores/market.store';
import { appStore } from '@/stores/app.store';
import { analyticsService } from '@/services/api/analytics.service';
import type { TimeInterval, QuantMetrics, CorrelationMatrix, AnomalyEvent } from '@/types/market';
import { formatPrice, formatNumber, formatUtcTime } from '@/utils/formatters';

export class MarketAnalyticsModule {
  private element: HTMLElement;
  private unsubscribeMarket?: () => void;
  private unsubscribeApp?: () => void;
  private chartContainer!: HTMLElement;
  private orderBookContainer!: HTMLElement;
  private quantContainer!: HTMLElement;
  private chart!: CandlestickChart;
  private quantMetrics: QuantMetrics | null = null;
  private correlation: CorrelationMatrix | null = null;
  private anomalies: AnomalyEvent[] = [];

  constructor() {
    this.element = createElement('div', { className: 'market-analytics-module anim-fade-in' });
  }

  public mount(parent: HTMLElement): void {
    parent.appendChild(this.element);
    this.buildLayout();

    this.unsubscribeMarket = marketStore.subscribe((state) => {
      if (state.klines.length > 0) {
        this.chart.setData(state.klines);
      }
      this.renderOrderBook();
    });

    this.unsubscribeApp = appStore.subscribe((state) => {
      marketStore.fetchMarketData(state.symbol);
      this.loadQuantData(state.symbol);
    });

    const activeSymbol = appStore.getState().symbol;
    marketStore.fetchMarketData(activeSymbol);
    this.loadQuantData(activeSymbol);
  }

  public unmount(): void {
    if (this.unsubscribeMarket) this.unsubscribeMarket();
    if (this.unsubscribeApp) this.unsubscribeApp();
    if (this.element.parentNode) this.element.parentNode.removeChild(this.element);
  }

  private async loadQuantData(symbol: string): Promise<void> {
    try {
      const [v, c, a] = await Promise.all([
        analyticsService.getVolatility(symbol),
        analyticsService.getCorrelationMatrix(),
        analyticsService.getAnomalies(5)
      ]);
      this.quantMetrics = v;
      this.correlation = c;
      this.anomalies = a;
      this.renderQuant();
    } catch {}
  }

  private buildLayout(): void {
    this.element.innerHTML = '';

    // Header Controls
    const topBar = createElement('div', {
      style: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '12px'
      }
    });

    const titleGroup = createElement('div');
    titleGroup.innerHTML = `
      <h2 style="font-size: 1.25rem; font-weight: 700;">Market Analytics & Real-Time Candlestick Chart</h2>
      <p style="font-size: 0.8rem; color: var(--text-muted);">
        Interactive OHLCV candlestick visualizer with sub-15ms Redis quotes and ClickHouse OLAP fallbacks.
      </p>
    `;
    topBar.appendChild(titleGroup);

    // Timeframe selector
    const timeframeGroup = createElement('div', { style: { display: 'flex', gap: '6px' } });
    const intervals: TimeInterval[] = ['1m', '5m', '15m', '1h', '4h', '1d'];

    for (const iv of intervals) {
      const btn = createButton({
        label: iv,
        size: 'sm',
        variant: marketStore.getState().activeInterval === iv ? 'primary' : 'secondary',
        onClick: () => {
          marketStore.setInterval(iv);
          marketStore.fetchMarketData(appStore.getState().symbol);
          this.buildLayout();
        }
      });
      timeframeGroup.appendChild(btn);
    }
    topBar.appendChild(timeframeGroup);
    this.element.appendChild(topBar);

    // Main Chart & Order Book Split
    const mainGrid = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'minmax(500px, 2.5fr) minmax(280px, 1fr)',
        gap: '16px',
        marginBottom: '20px'
      }
    });

    // Chart Card
    const chartCard = createElement('div', { className: 'card', style: { height: '460px', display: 'flex', flexDirection: 'column' } });
    const quote = marketStore.getState().quote;
    const priceDisplay = quote ? formatPrice(quote.price) : '$—';
    const changeDisplay = quote ? `${quote.change_24h_percent}%` : '0.00%';

    chartCard.innerHTML = `
      <div class="card-header" style="margin-bottom: 8px;">
        <div style="display: flex; align-items: baseline; gap: 12px;">
          <span style="font-size: 1.2rem; font-weight: 800;">${appStore.getState().symbol}</span>
          <span class="font-mono" style="font-size: 1.3rem; font-weight: 700; color: #10b981;">${priceDisplay}</span>
          <span class="badge ${parseFloat(changeDisplay) >= 0 ? 'badge-success' : 'badge-danger'}">${changeDisplay}</span>
        </div>
        <span class="badge badge-info">${marketStore.getState().activeInterval} Candle</span>
      </div>
    `;

    this.chartContainer = createElement('div', { style: { flex: '1', width: '100%', minHeight: '380px' } });
    chartCard.appendChild(this.chartContainer);
    mainGrid.appendChild(chartCard);

    this.chart = new CandlestickChart(this.chartContainer);

    // Order Book Card
    const obCard = createElement('div', { className: 'card', style: { height: '460px', display: 'flex', flexDirection: 'column' } });
    obCard.innerHTML = `
      <div class="card-header" style="margin-bottom: 8px;">
        <span class="card-title">Order Book (Depth Top 20)</span>
        <span class="badge badge-neutral">sub-15ms Redis</span>
      </div>
    `;
    this.orderBookContainer = createElement('div', { style: { flex: '1', overflowY: 'auto' } });
    obCard.appendChild(this.orderBookContainer);
    mainGrid.appendChild(obCard);

    this.element.appendChild(mainGrid);

    // Quantitative Analytics Section
    this.quantContainer = createElement('div', { style: { marginTop: '16px' } });
    this.element.appendChild(this.quantContainer);
  }

  private renderOrderBook(): void {
    const ob = marketStore.getState().orderBook;
    if (!ob) {
      this.orderBookContainer.innerHTML = '<div class="empty-state">No order book data</div>';
      return;
    }

    const bids = ob.bids.slice(0, 8);
    const asks = ob.asks.slice(0, 8).reverse();

    this.orderBookContainer.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.75rem; font-family: var(--font-mono);">
        <div style="display: flex; justify-content: space-between; color: var(--text-muted); font-size: 0.65rem; border-bottom: 1px solid var(--border-subtle); padding-bottom: 4px;">
          <span>PRICE (USD)</span>
          <span>SIZE</span>
        </div>

        <!-- Asks (Red) -->
        <div style="display: flex; flex-direction: column; gap: 2px;">
          ${asks.map(a => `
            <div style="display: flex; justify-content: space-between; color: var(--trade-sell); background: rgba(239, 68, 68, 0.05); padding: 2px 4px; border-radius: 2px;">
              <span>${formatNumber(a.price, 2)}</span>
              <span style="color: var(--text-secondary);">${formatNumber(a.quantity, 4)}</span>
            </div>
          `).join('')}
        </div>

        <!-- Mid Market Spread Indicator -->
        <div style="text-align: center; padding: 4px 0; font-weight: 700; color: var(--accent-primary); border-top: 1px dashed var(--border-subtle); border-bottom: 1px dashed var(--border-subtle);">
          MID: ${ob.bids[0] && ob.asks[0] ? formatPrice((parseFloat(ob.bids[0].price) + parseFloat(ob.asks[0].price)) / 2) : '—'}
        </div>

        <!-- Bids (Green) -->
        <div style="display: flex; flex-direction: column; gap: 2px;">
          ${bids.map(b => `
            <div style="display: flex; justify-content: space-between; color: var(--trade-buy); background: rgba(16, 185, 129, 0.05); padding: 2px 4px; border-radius: 2px;">
              <span>${formatNumber(b.price, 2)}</span>
              <span style="color: var(--text-secondary);">${formatNumber(b.quantity, 4)}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  private renderQuant(): void {
    this.quantContainer.innerHTML = '';
    const grid = createElement('div', {
      style: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '16px'
      }
    });

    // Quant Volatility Card
    const volCard = createElement('div', { className: 'card' });
    volCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Realized Volatility & Quant Math</span>
        <span class="badge badge-info">${this.quantMetrics?.window || '24h'} Window</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.8rem;">
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px;">
          <span style="color: var(--text-muted);">Annualized Realized Volatility:</span>
          <span class="font-mono" style="font-weight: 700; color: #10b981;">
            ${((this.quantMetrics?.realized_volatility_annualized || 0.45) * 100).toFixed(2)}%
          </span>
        </div>
        <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 6px;">
          <span style="color: var(--text-muted);">Log-Returns Std Deviation:</span>
          <span class="font-mono">${(this.quantMetrics?.log_returns_std || 0.012).toFixed(5)}</span>
        </div>
        <div style="display: flex; justify-content: space-between;">
          <span style="color: var(--text-muted);">Sample Size:</span>
          <span class="font-mono">${this.quantMetrics?.sample_count || 1440} ticks</span>
        </div>
      </div>
    `;
    grid.appendChild(volCard);

    // Correlation Matrix Card
    const corrCard = createElement('div', { className: 'card' });
    corrCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Pearson Correlation Matrix</span>
        <span class="badge badge-neutral">Cross-Asset</span>
      </div>
      <div style="overflow-x: auto;">
        <table style="width: 100%; font-size: 0.75rem; text-align: center; border-collapse: collapse;">
          <thead>
            <tr style="color: var(--text-muted); border-bottom: 1px solid var(--border-subtle);">
              <th style="padding: 4px; text-align: left;">Symbol</th>
              ${(this.correlation?.symbols || []).map(s => `<th style="padding: 4px;">${s.replace('USDT', '')}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${(this.correlation?.symbols || []).map((s, i) => `
              <tr style="border-bottom: 1px solid var(--border-subtle);">
                <td style="padding: 6px 4px; text-align: left; font-weight: 600;">${s.replace('USDT', '')}</td>
                ${(this.correlation?.matrix[i] || []).map(v => `
                  <td style="padding: 6px 4px; font-family: var(--font-mono); color: ${v > 0.7 ? '#60a5fa' : '#94a3b8'};">
                    ${v.toFixed(2)}
                  </td>
                `).join('')}
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
    grid.appendChild(corrCard);

    // Anomalies Card
    const anomCard = createElement('div', { className: 'card' });
    anomCard.innerHTML = `
      <div class="card-header">
        <span class="card-title">Statistical Market Anomalies</span>
        <span class="badge badge-warning">Z-Score > 3.0</span>
      </div>
      <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.75rem;">
        ${this.anomalies.map(a => `
          <div style="padding: 8px; background: rgba(245, 158, 11, 0.08); border-left: 3px solid #f59e0b; border-radius: var(--radius-sm);">
            <div style="display: flex; justify-content: space-between; font-weight: 600; margin-bottom: 2px;">
              <span>${a.symbol} · ${a.anomaly_type}</span>
              <span class="badge badge-warning">Z=${a.z_score.toFixed(1)}</span>
            </div>
            <div style="color: var(--text-secondary);">${a.description}</div>
            <div style="color: var(--text-muted); font-size: 0.65rem; margin-top: 4px;">${formatUtcTime(a.detected_at)}</div>
          </div>
        `).join('')}
      </div>
    `;
    grid.appendChild(anomCard);

    this.quantContainer.appendChild(grid);
  }
}
