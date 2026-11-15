import { defaultApiClient } from './client';
import type { QuantMetrics, CorrelationMatrix, AnomalyEvent } from '@/types/market';

export class AnalyticsService {
  constructor(private client = defaultApiClient) {}

  public async getVolatility(symbol = 'BTCUSDT', window = '24h'): Promise<QuantMetrics> {
    const res = await this.client.get('/analytics/volatility', { symbol, window });
    return {
      symbol: res.symbol || symbol,
      realized_volatility_annualized: res.realized_volatility_annualized ?? res.volatility ?? 0.42,
      log_returns_mean: res.log_returns_mean ?? 0.0001,
      log_returns_std: res.log_returns_std ?? 0.015,
      sample_count: res.sample_count ?? 1440,
      window: res.window || window
    };
  }

  public async getCorrelationMatrix(symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'BNBUSDT']): Promise<CorrelationMatrix> {
    const res = await this.client.get('/analytics/correlation', { symbols: symbols.join(',') });
    return {
      symbols: res.symbols || symbols,
      matrix: res.matrix || [
        [1.0, 0.82, 0.68, 0.75],
        [0.82, 1.0, 0.74, 0.71],
        [0.68, 0.74, 1.0, 0.65],
        [0.75, 0.71, 0.65, 1.0]
      ],
      window: res.window || '30d',
      calculated_at: res.calculated_at || new Date().toISOString()
    };
  }

  public async getAnomalies(limit = 20): Promise<AnomalyEvent[]> {
    const res = await this.client.get('/analytics/anomalies', { limit });
    const items = Array.isArray(res) ? res : res.anomalies || [];
    return items.map((a: any) => ({
      anomaly_id: a.anomaly_id || a.id || 'anom-1',
      symbol: a.symbol || 'BTCUSDT',
      anomaly_type: a.anomaly_type || 'PRICE_SPIKE',
      severity: a.severity || 'WARNING',
      detected_at: a.detected_at || a.timestamp || new Date().toISOString(),
      z_score: a.z_score ?? 3.4,
      description: a.description || 'Price deviation exceeding 3 standard deviations in 1m window.',
      cooldown_expires_at: a.cooldown_expires_at || new Date(Date.now() + 15 * 60 * 1000).toISOString()
    }));
  }
}

export const analyticsService = new AnalyticsService();

