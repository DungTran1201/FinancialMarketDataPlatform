import { defaultApiClient } from './client';
import type { QuantMetrics, CorrelationMatrix, AnomalyEvent } from '@/types/market';

export class AnalyticsService {
  constructor(private client = defaultApiClient) {}

  public async getVolatility(symbol = 'BTCUSDT', window = '24h'): Promise<QuantMetrics> {
    const raw = await this.client.get(`/analytics/statistics/${encodeURIComponent(symbol.toUpperCase())}`, { window });
    const res = raw?.data ?? raw ?? {};
    const vol = Number(res.realized_volatility_annualized ?? res.realized_volatility ?? res.volatility ?? 0);
    return {
      symbol: res.symbol || symbol,
      realized_volatility_annualized: Number.isFinite(vol) ? vol : 0,
      log_returns_mean: Number(res.log_returns_mean ?? 0),
      log_returns_std: Number(res.log_returns_std ?? 0),
      sample_count: Number(res.sample_count ?? res.trade_count ?? 0),
      window: res.window || window
    };
  }

  public async getCorrelationMatrix(symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']): Promise<CorrelationMatrix> {
    const raw = await this.client.get('/analytics/correlations', { symbols: symbols.join(',') });
    const res = raw?.data ?? raw ?? {};
    const syms: string[] = Array.isArray(res.symbols) ? res.symbols : symbols;
    let matrixRows: number[][];
    if (Array.isArray(res.matrix)) {
      matrixRows = res.matrix;
    } else if (res.matrix && typeof res.matrix === 'object') {
      matrixRows = syms.map((s1) => syms.map((s2) => Number(res.matrix?.[s1]?.[s2] ?? (s1 === s2 ? 1.0 : 0.0))));
    } else {
      matrixRows = syms.map((s1) => syms.map((s2) => (s1 === s2 ? 1.0 : 0.0)));
    }
    return {
      symbols: syms,
      matrix: matrixRows,
      window: res.window || '24h',
      calculated_at: res.calculated_at || new Date().toISOString()
    };
  }

  public async getAnomalies(limit = 20): Promise<AnomalyEvent[]> {
    const res = await this.client.get('/analytics/anomalies', { limit });
    const items = Array.isArray(res) ? res : res.data || res.anomalies || [];
    return items.map((a: any, idx: number) => ({
      anomaly_id: a.anomaly_id || a.id || `anom-${idx + 1}`,
      symbol: a.symbol || 'BTCUSDT',
      anomaly_type: a.anomaly_type || a.detector || 'PRICE_SPIKE',
      severity: a.severity || 'WARNING',
      detected_at: a.detected_at || a.timestamp || new Date().toISOString(),
      z_score: a.z_score ?? 0,
      description: a.description || `Detector ${a.detector || 'zscore'} z=${a.z_score ?? 0} (threshold=${a.threshold ?? 2.5})`,
      cooldown_expires_at: a.cooldown_expires_at || new Date(Date.now() + 15 * 60 * 1000).toISOString()
    }));
  }
}

export const analyticsService = new AnalyticsService();

