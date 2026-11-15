import type { RoutePath } from '@/types/navigation';
import { MainLayout } from '@/app/layouts/MainLayout';
import { DashboardModule } from '@/modules/dashboard/DashboardModule';
import { DataFlowModule } from '@/modules/data-flow/DataFlowModule';
import { MarketAnalyticsModule } from '@/modules/market-analytics/MarketAnalyticsModule';
import { DataManagementModule } from '@/modules/data-management/DataManagementModule';
import { AiWorkspaceModule } from '@/modules/ai-workspace/AiWorkspaceModule';
import { AdministrationModule } from '@/modules/administration/AdministrationModule';

export interface RouteModule {
  mount: (parent: HTMLElement) => void;
  unmount: () => void;
}

export class AppRouter {
  private layout: MainLayout;
  private currentModule: RouteModule | null = null;
  private routes: Map<RoutePath, () => RouteModule> = new Map();

  constructor(layout: MainLayout) {
    this.layout = layout;
    this.registerRoutes();
    this.bindEvents();
  }

  private registerRoutes(): void {
    this.routes.set('/', () => new DashboardModule());
    this.routes.set('/dashboard', () => new DashboardModule());
    this.routes.set('/data-flow', () => new DataFlowModule());
    this.routes.set('/market-analytics', () => new MarketAnalyticsModule());
    this.routes.set('/data-management', () => new DataManagementModule());
    this.routes.set('/ai-workspace', () => new AiWorkspaceModule());
    this.routes.set('/administration', () => new AdministrationModule());
  }

  private bindEvents(): void {
    window.addEventListener('hashchange', () => {
      this.handleRoute();
    });
  }

  public init(): void {
    if (!window.location.hash) {
      window.location.hash = '#/dashboard';
    } else {
      this.handleRoute();
    }
  }

  private handleRoute(): void {
    const raw = window.location.hash.slice(1);
    const hash = (raw || '/dashboard') as RoutePath;

    // Normalize route
    const factory = this.routes.get(hash) || this.routes.get('/dashboard')!;
    const cleanPath = (this.routes.has(hash) ? hash : '/dashboard') as RoutePath;

    // Unmount previous module
    if (this.currentModule) {
      try {
        this.currentModule.unmount();
      } catch (err) {
        console.error('Error unmounting module:', err);
      }
      this.currentModule = null;
    }

    // Update layout navigation state
    this.layout.setRoute(cleanPath);

    // Mount new module
    const viewport = this.layout.getContentViewport();
    viewport.innerHTML = '';

    try {
      this.currentModule = factory();
      this.currentModule.mount(viewport);
    } catch (err) {
      console.error(`Error mounting route [${cleanPath}]:`, err);
      viewport.innerHTML = `<div class="error-state">Failed to render route: ${cleanPath}</div>`;
    }
  }
}
