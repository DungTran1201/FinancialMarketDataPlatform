import './styles/main.css';
import { MainLayout } from '@/app/layouts/MainLayout';
import { AppRouter } from '@/app/router/router';
import { sseClient } from '@/services/api/sse';
import { wsClient } from '@/services/websocket/ws-client';

document.addEventListener('DOMContentLoaded', () => {
  const root = document.getElementById('app');
  if (!root) return;

  // 1. Initialize Layout Shell
  const layout = new MainLayout();
  root.innerHTML = '';
  root.appendChild(layout.getElement());

  // 2. Initialize Routing System
  const router = new AppRouter(layout);
  router.init();

  // 3. Connect Real-Time Telemetry & WebSocket Streams
  sseClient.connect();
  wsClient.connect();

  console.info('🚀 FinancialMarketDataPlatform — Experience Layer Initialized');
});
