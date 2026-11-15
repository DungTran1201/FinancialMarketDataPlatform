export type SymbolKey = 'BTCUSDT' | 'ETHUSDT' | 'SOLUSDT' | 'BNBUSDT' | 'ADAUSDT';
export type TimeInterval = '1m' | '5m' | '15m' | '1h' | '4h' | '1d';

export interface PriceQuote {
  provider: string;
  symbol: string;
  price: string;
  bid: string;
  ask: string;
  volume_24h: string;
  high_24h: string;
  low_24h: string;
  change_24h_percent: string;
  event_time: string;
  source: 'REDIS_HOT' | 'CLICKHOUSE_OLAP' | 'BINANCE_REST';
}

export interface OrderBookLevel {
  price: string;
  quantity: string;
  total?: string;
}

export interface OrderBookSnapshot {
  provider: string;
  symbol: string;
  timestamp: string;
  bids: OrderBookLevel[];
  asks: OrderBookLevel[];
  sequence_id: number;
}

export interface KlineCandle {
  symbol: string;
  interval: TimeInterval;
  open_time: number;
  close_time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  trades_count: number;
  is_closed: boolean;
}

export interface QuantMetrics {
  symbol: string;
  realized_volatility_annualized: number;
  log_returns_mean: number;
  log_returns_std: number;
  sample_count: number;
  window: string;
}

export interface CorrelationMatrix {
  symbols: string[];
  matrix: number[][];
  window: string;
  calculated_at: string;
}

export interface AnomalyEvent {
  anomaly_id: string;
  symbol: string;
  anomaly_type: 'PRICE_SPIKE' | 'VOLUME_SURGE' | 'SPREAD_BLOWOUT' | 'LATENCY_SPIKE';
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  detected_at: string;
  z_score: number;
  description: string;
  cooldown_expires_at: string;
}

