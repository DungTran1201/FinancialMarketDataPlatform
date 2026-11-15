"""Real-Time 12-Stage Data Flow & Latency Observatory Frontend UI (`SCR-001` / `/ui/data-flow`)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

if TYPE_CHECKING:
    from src.serving.infrastructure.runtime import PlatformRuntimeContainer


DATA_FLOW_OBSERVATORY_HTML = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FMDP — Real-Time Data Flow & Latency Observatory (12 Stages)</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-slate-950 text-slate-100 antialiased min-h-screen p-6">
  <div class="max-w-7xl mx-auto space-y-6">
    <!-- Top Header & Live Controls -->
    <header class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-xs font-mono uppercase tracking-wider text-emerald-400">
            LIVE REAL-TIME TELEMETRY STREAM (ZERO-MOCK v0.1)
          </span>
        </div>
        <h1 class="text-2xl font-bold tracking-tight mt-1">
          Real-Time Data Flow &amp; End-to-End Latency Observatory
        </h1>
        <p class="text-xs text-slate-400 mt-0.5">
          Luồng dữ liệu trực quan 12 bước: Ingestion &rarr; Kafka &rarr; MinIO &rarr; Redis/ClickHouse &rarr; Monitoring
        </p>
      </div>
      <div class="flex items-center gap-3">
        <label
          class="text-xs text-slate-400 flex items-center gap-2 bg-slate-900 border border-slate-800 p-2 rounded">
          Chu kỳ làm mới:
          <select id="pollInterval" class="bg-slate-800 text-slate-100 rounded px-2 py-0.5 text-xs font-mono">
            <option value="500">500 ms</option>
            <option value="1000" selected>1000 ms</option>
            <option value="2000">2000 ms</option>
          </select>
        </label>
        <button id="btnRunPipeline"
          class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3.5 py-2 rounded-lg">
          Chạy lại Full 12-Stage Pipeline
        </button>
      </div>
    </header>

    <!-- KPI Summary Cards (Total Ingestion -> Monitoring Calculation) -->
    <section class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
        <div class="text-xs text-slate-400">Tổng thời gian xử lý (Ingestion &rarr; Monitoring)</div>
        <div id="kpiIngestToMonitor" class="text-2xl font-mono font-bold text-emerald-400 mt-1">-- ms</div>
        <div id="kpiTotal12Stages" class="text-xs font-mono text-slate-400 mt-1">Toàn trình 12 Stage: -- ms</div>
      </div>
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
        <div class="text-xs text-slate-400">Độ trễ Nguồn Thực tế (Exchange &rarr; Ingestion)</div>
        <div id="kpiSourceLag" class="text-2xl font-mono font-bold text-sky-400 mt-1">-- ms</div>
        <div id="kpiE2ELag" class="text-xs font-mono text-slate-400 mt-1">Tổng độ trễ E2E thực tế: -- ms</div>
      </div>
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
        <div class="text-xs text-slate-400">Ngân sách SLA (Mục tiêu &le; 200 ms)</div>
        <div id="kpiSlaPct" class="text-2xl font-mono font-bold text-amber-400 mt-1">-- %</div>
        <div class="w-full bg-slate-800 h-2 rounded-full mt-2 overflow-hidden">
          <div id="kpiSlaBar" class="bg-emerald-500 h-full transition-all duration-300" style="width: 15%"></div>
        </div>
      </div>
      <div class="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
        <div class="text-xs text-slate-400">Tiến trình Pipeline &amp; Kiểm soát Chất lượng</div>
        <div id="kpiProgress" class="text-2xl font-mono font-bold text-indigo-400 mt-1">100% (12/12)</div>
        <div id="kpiCounters" class="text-xs font-mono text-slate-400 mt-1">Hot Updates: -- | DLQ: 0</div>
      </div>
    </section>

    <!-- Live Market Source Streams Table -->
    <section class="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-300">
          Nguồn Dữ liệu Thực tế Đang Cập nhật Liên tục (Exchange Live Feed)
        </h2>
        <span id="lastSampledAt" class="text-xs font-mono text-slate-400">--</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs font-mono">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400">
              <th class="pb-2">Nguồn (Provider)</th>
              <th class="pb-2">Cặp Giao dịch</th>
              <th class="pb-2">Giá Thực tế (Last Price)</th>
              <th class="pb-2">Thời gian Khớp lệnh (Exchange UTC)</th>
              <th class="pb-2">Độ trễ Nguồn (Source Lag)</th>
              <th class="pb-2">Trạng thái Luồng</th>
            </tr>
          </thead>
          <tbody id="liveSourcesBody" class="divide-y divide-slate-800/60"></tbody>
        </table>
      </div>
    </section>

    <!-- 12-Stage Visual Data Flow & Latency Waterfall -->
    <section class="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-300">
          Chi tiết 12 Bước Xử lý Luồng Dữ liệu (Stage-by-Stage Processing &amp; Cumulative Time)
        </h2>
        <span class="text-xs font-mono text-emerald-400">Công thức: T_total = &Sigma;(T_stage_1 .. T_stage_11)</span>
      </div>
      <div id="stagesGrid" class="grid grid-cols-1 md:grid-cols-3 gap-3"></div>
    </section>
  </div>

  <script>
    let timerId = null;

    async function fetchTelemetry() {
      try {
        const res = await fetch('/api/v1/data-platform/v01/telemetry');
        if (!res.ok) return;
        const data = await res.json();
        renderTelemetry(data);
      } catch (err) {
        console.error('Telemetry fetch error:', err);
      }
    }

    function renderTelemetry(data) {
      const sm = data.summary_metrics;
      const tIngestMon = sm.total_ingestion_to_monitoring_ms.toFixed(2);
      const t12Stages = sm.total_12_stages_processing_ms.toFixed(2);
      const tSrcLag = sm.source_to_ingestion_lag_ms.toFixed(2);
      const tE2eLag = sm.end_to_end_source_to_monitoring_lag_ms.toFixed(2);
      document.getElementById('kpiIngestToMonitor').textContent = tIngestMon + ' ms';
      document.getElementById('kpiTotal12Stages').textContent = 'Toàn trình 12 Stage: ' + t12Stages + ' ms';
      document.getElementById('kpiSourceLag').textContent = tSrcLag + ' ms';
      document.getElementById('kpiE2ELag').textContent = 'Tổng độ trễ E2E thực tế: ' + tE2eLag + ' ms';
      document.getElementById('kpiSlaPct').textContent = sm.sla_utilization_pct.toFixed(1) + '% / 200ms';
      document.getElementById('kpiSlaBar').style.width = Math.min(100, sm.sla_utilization_pct) + '%';
      document.getElementById('kpiCounters').textContent =
        'Hot Updates: ' + sm.hot_redis_applied_updates + ' | DLQ: ' + sm.dlq_routed_events;
      document.getElementById('lastSampledAt').textContent =
        'Tick #' + data.telemetry_sequence + ' | ' + data.sampled_at;

      const tbody = document.getElementById('liveSourcesBody');
      tbody.innerHTML = data.live_sources.map(src => `
        <tr class="hover:bg-slate-800/40">
          <td class="py-2 text-slate-300 uppercase">${src.provider}</td>
          <td class="py-2 font-bold text-white">${src.symbol}</td>
          <td class="py-2 text-emerald-400 font-bold">$${src.last_price}</td>
          <td class="py-2 text-slate-400">${src.exchange_event_time}</td>
          <td class="py-2 text-sky-400">${src.source_lag_ms.toFixed(2)} ms</td>
          <td class="py-2">
            <span class="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[11px]">
              ${src.stream_status}
            </span>
          </td>
        </tr>
      `).join('');

      const stagesGrid = document.getElementById('stagesGrid');
      stagesGrid.innerHTML = data.stages.map(st => `
        <div class="bg-slate-950/80 border border-slate-800 rounded-lg p-3 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between text-xs">
              <span class="font-bold text-slate-100">${st.name}</span>
              <span class="font-mono px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300">${st.status}</span>
            </div>
            <div class="text-[11px] text-slate-400 mt-1">${st.technology}</div>
            <div class="text-[11px] font-mono text-slate-300 mt-1 truncate">Artifact: ${st.artifact}</div>
          </div>
          <div class="mt-3 pt-2 border-t border-slate-800/80 space-y-1.5">
            <div class="flex justify-between text-xs font-mono">
              <span class="text-slate-400">
                Xử lý Stage: <strong class="text-emerald-400">${st.processing_ms.toFixed(2)} ms</strong>
              </span>
              <span class="text-slate-400">
                Lũy kế: <strong class="text-amber-300">${st.cumulative_elapsed_ms.toFixed(2)} ms</strong>
              </span>
            </div>
            <div class="flex justify-between text-[11px] font-mono text-slate-400">
              <span>Độ trễ nguồn: ${st.source_lag_ms.toFixed(1)} ms</span>
              <span>Bản ghi: ${st.records_processed}</span>
            </div>
            <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
              <div class="bg-indigo-500 h-full" style="width: ${st.progress_pct}%"></div>
            </div>
          </div>
        </div>
      `).join('');
    }

    document.getElementById('btnRunPipeline').addEventListener('click', async () => {
      await fetch('/api/v1/data-platform/v01/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbols: ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'], interval: '1m', backfill_minutes: 6 })
      });
      await fetchTelemetry();
    });

    document.getElementById('pollInterval').addEventListener('change', (e) => {
      if (timerId) clearInterval(timerId);
      timerId = setInterval(fetchTelemetry, Number(e.target.value));
    });

    fetchTelemetry();
    timerId = setInterval(fetchTelemetry, 1000);
  </script>
</body>
</html>
"""


def build_frontend_ui_router(runtime: PlatformRuntimeContainer) -> APIRouter:
    """Build `/ui` router serving the interactive Real-Time Data Flow Observatory (`SCR-001`)."""
    router = APIRouter()
    _ = runtime

    @router.get("/data-flow", response_class=HTMLResponse)
    async def render_data_flow_observatory() -> HTMLResponse:
        """Render the interactive 12-Stage Real-Time Data Flow & Latency Observatory UI (`SCR-001`)."""
        return HTMLResponse(content=DATA_FLOW_OBSERVATORY_HTML, status_code=200)

    return router
