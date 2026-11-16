import { defaultApiClient } from './client';
import type { PriceQuote, OrderBookSnapshot, KlineCandle, TimeInterval } from '@/types/market';

export class MarketService {
  constructor(private client = defaultApiClient) {}

  public async getLatestPrice(symbol: string, provider = 'binance'): Promise<PriceQuote> {
    const res = await this.client.get(`/market/prices/${encodeURIComponent(symbol.toUpperCase())}`, { provider });
    const data = res?.data ?? res ?? {};
    const meta = res?.meta ?? {};
    return {
      provider: data.provider || provider,
      symbol: data.symbol || symbol,
      price: String(data.price || data.last_price || '0'),
      bid: String(data.bid || '0'),
      ask: String(data.ask || '0'),
      volume_24h: String(data.volume_24h || data.volume || '0'),
      high_24h: String(data.high_24h || '0'),
      low_24h: String(data.low_24h || '0'),
      change_24h_percent: String(data.change_24h_percent || '0'),
      event_time: data.exchange_event_time || data.event_time || data.timestamp || new Date().toISOString(),
      source: data.source || meta.source || 'REDIS_HOT'
    };
  }

  public async getOrderBook(symbol: string, limit = 20): Promise<OrderBookSnapshot> {
    const depth = Math.max(5, Math.min(20, limit));
    const res = await this.client.get(`/market/orderbook/${encodeURIComponent(symbol.toUpperCase())}`, { depth });
    const data = res?.data ?? res ?? {};
    return {
      provider: data.provider || 'binance',
      symbol: data.symbol || symbol,
      timestamp: data.exchange_event_time || data.timestamp || new Date().toISOString(),
      bids: (data.bids || []).map((b: any) => ({
        price: Array.isArray(b) ? String(b[0]) : String(b.price),
        quantity: Array.isArray(b) ? String(b[1]) : String(b.quantity)
      })),
      asks: (data.asks || []).map((a: any) => ({
        price: Array.isArray(a) ? String(a[0]) : String(a.price),
        quantity: Array.isArray(a) ? String(a[1]) : String(a.quantity)
      })),
      sequence_id: data.sequence_id || 0
    };
  }

  public async getHistoricalKlines(
    symbol: string,
    interval: TimeInterval = '1m',
    limit = 60
  ): Promise<KlineCandle[]> {
    const res = await this.client.get(`/historical/klines/${encodeURIComponent(symbol.toUpperCase())}`, {
      interval,
      limit
    });
    const items = Array.isArray(res) ? res : res.candles || res.data || [];
    return items.map((c: any) => ({
      symbol: c.symbol || symbol,
      interval: (c.interval || interval) as TimeInterval,
      open_time: typeof c.open_time === 'number' ? c.open_time : new Date(c.open_time || c.timestamp || 0).getTime(),
      close_time: typeof c.close_time === 'number' ? c.close_time : new Date(c.close_time || 0).getTime(),
      open: parseFloat(c.open || c.open_price || '0'),
      high: parseFloat(c.high || c.high_price || '0'),
      low: parseFloat(c.low || c.low_price || '0'),
      close: parseFloat(c.close || c.close_price || '0'),
      volume: parseFloat(c.volume || c.base_volume || '0'),
      trades_count: c.trades_count || c.trade_count || c.count || 0,
      is_closed: c.is_closed ?? true
    }));
  }
}

export const marketService = new MarketService();

