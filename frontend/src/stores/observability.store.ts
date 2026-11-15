import type {
  ObservabilityKPIs,
  SystemTopology,
  EventLifecycleTrace,
  ParallelBranchLatency
} from '@/types/observability';
import { observabilityService } from '@/services/api/observability.service';
import { sseClient } from '@/services/api/sse';

export interface ObservabilityState {
  kpis: ObservabilityKPIs | null;
  topology: SystemTopology | null;
  traces: EventLifecycleTrace[];
  latencies: ParallelBranchLatency | null;
  selectedTrace: EventLifecycleTrace | null;
  platformStatus: string;
  loading: boolean;
  error: string | null;
}

type Listener = (state: ObservabilityState) => void;

class ObservabilityStore {
  private state: ObservabilityState = {
    kpis: null,
    topology: null,
    traces: [],
    latencies: null,
    selectedTrace: null,
    platformStatus: 'HEALTHY',
    loading: false,
    error: null
  };

  private listeners: Set<Listener> = new Set();
  private sseUnsubscribe: (() => void) | null = null;

  public getState(): ObservabilityState {
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
      try { l(s); } catch (err) { console.error('Error in ObservabilityStore listener:', err); }
    }
  }

  public selectTrace(trace: EventLifecycleTrace | null): void {
    this.state.selectedTrace = trace;
    this.notify();
  }

  public async loadInitial(): Promise<void> {
    this.state.loading = true;
    this.state.error = null;
    this.notify();

    try {
      const [overview, topology, traces, latencies] = await Promise.all([
        observabilityService.getOverview('1h'),
        observabilityService.getTopology(),
        observabilityService.getTraces(20),
        observabilityService.getLatencyPercentiles()
      ]);

      this.state.kpis = overview.kpis;
      this.state.platformStatus = overview.platform_status;
      this.state.topology = topology;
      this.state.traces = traces;
      this.state.latencies = latencies;
      this.state.loading = false;
      this.notify();
    } catch (err: any) {
      this.state.loading = false;
      this.state.error = err.message || 'Failed to load observability data';
      this.notify();
    }
  }

  public initSseStream(): void {
    if (this.sseUnsubscribe) return;

    sseClient.connect();

    const unsubPulse = sseClient.on('pulse', (data: any) => {
      if (data.kpis) {
        this.state.kpis = { ...this.state.kpis, ...data.kpis };
      }
      if (data.topology) {
        this.state.topology = data.topology;
      }
      this.notify();
    });

    const unsubTrace = sseClient.on('trace', (trace: EventLifecycleTrace) => {
      this.state.traces = [trace, ...this.state.traces.slice(0, 49)];
      this.notify();
    });

    this.sseUnsubscribe = () => {
      unsubPulse();
      unsubTrace();
    };
  }

  public cleanupSse(): void {
    if (this.sseUnsubscribe) {
      this.sseUnsubscribe();
      this.sseUnsubscribe = null;
    }
  }
}

export const observabilityStore = new ObservabilityStore();

