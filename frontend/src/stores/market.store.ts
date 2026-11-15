import type { PriceQuote, OrderBookSnapshot, KlineCandle, TimeInterval } from '@/types/market';
import { marketService } from '@/services/api/market.service';

export interface MarketState {
  quote: PriceQuote | null;
  orderBook: OrderBookSnapshot | null;
  klines: KlineCandle[];
  activeInterval: TimeInterval;
  loading: boolean;
  error: string | null;
}

type Listener = (state: MarketState) => void;

class MarketStore {
  private state: MarketState = {
    quote: null,
    orderBook: null,
    klines: [],
    activeInterval: '1m',
    loading: false,
    error: null
  };

  private listeners: Set<Listener> = new Set();

  public getState(): MarketState {
    return { ...this.state };
  }

  public subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener(this.getState());
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    const s = this.getState();
    for (const l of this.listeners) {
      try { l(s); } catch (err) { console.error('Error in MarketStore listener:', err); }
    }
  }

  public setInterval(interval: TimeInterval): void {
    this.state.activeInterval = interval;
    this.notify();
  }

  public async fetchMarketData(symbol: string): Promise<void> {
    this.state.loading = true;
    this.state.error = null;
    this.notify();

    try {
      const [quote, orderBook, klines] = await Promise.all([
        marketService.getLatestPrice(symbol),
        marketService.getOrderBook(symbol, 20),
        marketService.getHistoricalKlines(symbol, this.state.activeInterval, 60)
      ]);

      this.state.quote = quote;
      this.state.orderBook = orderBook;
      this.state.klines = klines;
      this.state.loading = false;
      this.notify();
    } catch (err: any) {
      this.state.loading = false;
      this.state.error = err.message || 'Failed to load market data';
      this.notify();
    }
  }

  public updateQuote(quote: PriceQuote): void {
    this.state.quote = quote;
    this.notify();
  }
}

export const marketStore = new MarketStore();

