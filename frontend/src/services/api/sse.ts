export type SseEventHandler<T = any> = (data: T) => void;

export class SseStreamClient {
  private eventSource: EventSource | null = null;
  private listeners: Map<string, Set<SseEventHandler>> = new Map();
  private reconnectTimer: any = null;
  private url: string;
  private active = false;

  constructor(url = '/api/v1/observability/stream') {
    this.url = url;
  }

  public connect(): void {
    if (this.active) return;
    this.active = true;

    try {
      this.eventSource = new EventSource(this.url);

      this.eventSource.onopen = () => {
        this.emit('connection', { status: 'CONNECTED' });
      };

      this.eventSource.onerror = (err) => {
        this.emit('connection', { status: 'ERROR', error: err });
        this.cleanup();
        this.scheduleReconnect();
      };

      this.eventSource.addEventListener('snapshot', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          this.emit('snapshot', data);
        } catch {}
      });

      this.eventSource.addEventListener('pulse', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          this.emit('pulse', data);
        } catch {}
      });

      this.eventSource.addEventListener('trace', (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          this.emit('trace', data);
        } catch {}
      });
    } catch (e) {
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.active = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.cleanup();
    this.emit('connection', { status: 'DISCONNECTED' });
  }

  private cleanup(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }

  private scheduleReconnect(): void {
    if (!this.active || this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (this.active) this.connect();
    }, 3000);
  }

  public on(event: string, handler: SseEventHandler): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
    return () => this.off(event, handler);
  }

  public off(event: string, handler: SseEventHandler): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  private emit(event: string, data: any): void {
    const handlers = this.listeners.get(event);
    if (handlers) {
      for (const h of handlers) {
        try {
          h(data);
        } catch (err) {
          console.error(`Error in SSE listener for '${event}':`, err);
        }
      }
    }
  }
}

export const sseClient = new SseStreamClient('/api/v1/observability/stream');

