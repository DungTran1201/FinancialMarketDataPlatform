import type { SymbolKey } from '@/types/market';
import type { UserProfile } from '@/types/auth';
import { authService } from '@/services/auth/auth.service';

export type ConnectionState = 'CONNECTED' | 'CONNECTING' | 'DISCONNECTED' | 'ERROR';
export type ExecutionMode = 'LIVE' | 'DEMO';

export interface AppNotification {
  id: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  message: string;
  timestamp: string;
}

export interface AppState {
  symbol: SymbolKey;
  mode: ExecutionMode;
  connection: ConnectionState;
  sidebarCollapsed: boolean;
  currentUser: UserProfile | null;
  notifications: AppNotification[];
}

type Listener = (state: AppState) => void;

class AppStore {
  private state: AppState = {
    symbol: 'BTCUSDT',
    mode: 'LIVE',
    connection: 'DISCONNECTED',
    sidebarCollapsed: false,
    currentUser: authService.getUser(),
    notifications: []
  };

  private listeners: Set<Listener> = new Set();

  public getState(): AppState {
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
      try { l(s); } catch (err) { console.error('Error in AppStore listener:', err); }
    }
  }

  public setSymbol(symbol: SymbolKey): void {
    this.state.symbol = symbol;
    this.notify();
  }

  public setMode(mode: ExecutionMode): void {
    this.state.mode = mode;
    this.notify();
  }

  public setConnection(connection: ConnectionState): void {
    this.state.connection = connection;
    this.notify();
  }

  public toggleSidebar(): void {
    this.state.sidebarCollapsed = !this.state.sidebarCollapsed;
    this.notify();
  }

  public addNotification(type: AppNotification['type'], message: string): void {
    const notif: AppNotification = {
      id: Math.random().toString(36).substring(2, 9),
      type,
      message,
      timestamp: new Date().toISOString()
    };
    this.state.notifications = [notif, ...this.state.notifications.slice(0, 19)];
    this.notify();
  }

  public clearNotifications(): void {
    this.state.notifications = [];
    this.notify();
  }
}

export const appStore = new AppStore();

