export type WsMessageHandler = (msg: any) => void;

export class ResilientWebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private isConnecting = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private pingInterval: any = null;
  private listeners: Map<string, Set<WsMessageHandler>> = new Map();
  private connectionListeners: Set<(connected: boolean) => void> = new Set();

  constructor(path = '/ws/v1/observability/stream') {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.url = `${protocol}//${window.location.host}${path}`;
  }

  public get connecting(): boolean {
    return this.isConnecting;
  }

  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;
    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.notifyConnectionState(true);
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          const type = parsed.type || parsed.event || 'message';
          this.emit(type, parsed.data || parsed);
        } catch {
          this.emit('raw', event.data);
        }
      };

      this.ws.onclose = () => {
        this.cleanup();
        this.notifyConnectionState(false);
        this.scheduleReconnect();
      };

      this.ws.onerror = () => {
        this.cleanup();
        this.notifyConnectionState(false);
      };
    } catch {
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.cleanup();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.notifyConnectionState(false);
  }

  public send(type: string, data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
      }
    }, 15000);
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private cleanup(): void {
    this.isConnecting = false;
    this.stopHeartbeat();
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts), 15000);
    setTimeout(() => this.connect(), delay);
  }

  public onConnectionChange(listener: (connected: boolean) => void): () => void {
    this.connectionListeners.add(listener);
    return () => this.connectionListeners.delete(listener);
  }

  private notifyConnectionState(connected: boolean): void {
    for (const l of this.connectionListeners) {
      try { l(connected); } catch {}
    }
  }

  public on(type: string, handler: WsMessageHandler): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)!.add(handler);
    return () => this.off(type, handler);
  }

  public off(type: string, handler: WsMessageHandler): void {
    const handlers = this.listeners.get(type);
    if (handlers) handlers.delete(handler);
  }

  private emit(type: string, data: any): void {
    const handlers = this.listeners.get(type);
    if (handlers) {
      for (const h of handlers) {
        try { h(data); } catch (err) { console.error(`WS Handler error [${type}]:`, err); }
      }
    }
  }
}

export const wsClient = new ResilientWebSocketClient('/ws/v1/observability/stream');
