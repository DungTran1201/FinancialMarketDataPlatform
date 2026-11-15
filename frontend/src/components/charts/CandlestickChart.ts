import type { KlineCandle } from '@/types/market';
import { createElement } from '@/utils/dom';
import { formatPrice, formatNumber } from '@/utils/formatters';

export class CandlestickChart {
  private container: HTMLElement;
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private data: KlineCandle[] = [];
  private hoveredCandle: KlineCandle | null = null;
  private mouseX = -1;
  private mouseY = -1;

  constructor(container: HTMLElement) {
    this.container = container;
    this.canvas = createElement('canvas', {
      style: {
        width: '100%',
        height: '100%',
        display: 'block'
      }
    });
    this.container.appendChild(this.canvas);
    this.ctx = this.canvas.getContext('2d')!;

    this.bindEvents();
    this.resize();
  }

  public setData(data: KlineCandle[]): void {
    this.data = [...data];
    this.render();
  }

  private bindEvents(): void {
    window.addEventListener('resize', () => {
      this.resize();
      this.render();
    });

    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      this.mouseX = (e.clientX - rect.left) * (this.canvas.width / rect.width);
      this.mouseY = (e.clientY - rect.top) * (this.canvas.height / rect.height);
      this.render();
    });

    this.canvas.addEventListener('mouseleave', () => {
      this.mouseX = -1;
      this.mouseY = -1;
      this.hoveredCandle = null;
      this.render();
    });
  }

  private resize(): void {
    const dpr = window.devicePixelRatio || 1;
    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 400;

    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  public render(): void {
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;

    if (!width || !height || this.data.length === 0) {
      this.ctx.clearRect(0, 0, width, height);
      this.ctx.fillStyle = '#64748b';
      this.ctx.font = '13px sans-serif';
      this.ctx.textAlign = 'center';
      this.ctx.fillText('No candlestick data available', width / 2, height / 2);
      return;
    }

    const dpr = window.devicePixelRatio || 1;
    this.ctx.clearRect(0, 0, width, height);

    // Padding
    const padTop = 20;
    const padBottom = 60;
    const padRight = 70;
    const padLeft = 10;
    const chartHeight = height - padTop - padBottom;
    const volumeHeight = 50;
    const priceHeight = chartHeight - volumeHeight - 10;

    // Price Bounds
    let minPrice = Infinity;
    let maxPrice = -Infinity;
    let maxVol = 0;

    for (const c of this.data) {
      if (c.low < minPrice) minPrice = c.low;
      if (c.high > maxPrice) maxPrice = c.high;
      if (c.volume > maxVol) maxVol = c.volume;
    }

    if (minPrice === maxPrice) {
      minPrice *= 0.99;
      maxPrice *= 1.01;
    }
    const priceRange = maxPrice - minPrice;

    // Grid Lines
    this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    this.ctx.lineWidth = 1;
    const gridLines = 5;
    this.ctx.fillStyle = '#64748b';
    this.ctx.font = '10px monospace';
    this.ctx.textAlign = 'left';

    for (let i = 0; i <= gridLines; i++) {
      const y = padTop + (priceHeight / gridLines) * i;
      const priceVal = maxPrice - (priceRange / gridLines) * i;
      this.ctx.beginPath();
      this.ctx.moveTo(padLeft, y);
      this.ctx.lineTo(width - padRight, y);
      this.ctx.stroke();

      this.ctx.fillText(formatPrice(priceVal), width - padRight + 6, y + 3);
    }

    // Candle layout
    const count = this.data.length;
    const slotWidth = (width - padLeft - padRight) / count;
    const candleWidth = Math.max(2, slotWidth * 0.7);

    let activeHoverIndex = -1;
    if (this.mouseX > 0) {
      const mouseCssX = this.mouseX / dpr;
      if (mouseCssX >= padLeft && mouseCssX <= width - padRight) {
        activeHoverIndex = Math.min(count - 1, Math.max(0, Math.floor((mouseCssX - padLeft) / slotWidth)));
        this.hoveredCandle = this.data[activeHoverIndex];
      }
    }

    // Render Candles & Volumes
    for (let i = 0; i < count; i++) {
      const c = this.data[i];
      const x = padLeft + i * slotWidth + slotWidth / 2;
      const isUp = c.close >= c.open;
      const color = isUp ? '#10b981' : '#ef4444';

      // 1. Volume Bar
      const vH = maxVol > 0 ? (c.volume / maxVol) * volumeHeight : 0;
      const vY = height - padBottom - vH;
      this.ctx.fillStyle = isUp ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)';
      this.ctx.fillRect(x - candleWidth / 2, vY, candleWidth, vH);

      // 2. Candlestick Wick (High/Low)
      const yHigh = padTop + ((maxPrice - c.high) / priceRange) * priceHeight;
      const yLow = padTop + ((maxPrice - c.low) / priceRange) * priceHeight;

      this.ctx.strokeStyle = color;
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.moveTo(x, yHigh);
      this.ctx.lineTo(x, yLow);
      this.ctx.stroke();

      // 3. Candlestick Body
      const yOpen = padTop + ((maxPrice - c.open) / priceRange) * priceHeight;
      const yClose = padTop + ((maxPrice - c.close) / priceRange) * priceHeight;
      const bodyY = Math.min(yOpen, yClose);
      const bodyH = Math.max(1.5, Math.abs(yClose - yOpen));

      this.ctx.fillStyle = color;
      this.ctx.fillRect(x - candleWidth / 2, bodyY, candleWidth, bodyH);
    }

    // Crosshair & Tooltip
    if (this.hoveredCandle && activeHoverIndex >= 0) {
      const c = this.hoveredCandle;
      const x = padLeft + activeHoverIndex * slotWidth + slotWidth / 2;
      const mouseCssY = this.mouseY / dpr;

      // Vertical line
      this.ctx.strokeStyle = 'rgba(148, 163, 184, 0.4)';
      this.ctx.setLineDash([4, 4]);
      this.ctx.beginPath();
      this.ctx.moveTo(x, padTop);
      this.ctx.lineTo(x, height - padBottom + volumeHeight);
      this.ctx.stroke();

      // Horizontal line
      if (mouseCssY >= padTop && mouseCssY <= padTop + priceHeight) {
        this.ctx.beginPath();
        this.ctx.moveTo(padLeft, mouseCssY);
        this.ctx.lineTo(width - padRight, mouseCssY);
        this.ctx.stroke();
      }
      this.ctx.setLineDash([]);

      // Floating Tooltip
      const dateStr = new Date(c.open_time).toLocaleTimeString();
      const tipText = `${dateStr} | O: ${c.open} H: ${c.high} L: ${c.low} C: ${c.close} | Vol: ${formatNumber(c.volume, 2)}`;

      this.ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
      this.ctx.fillRect(padLeft + 4, padTop + 4, 340, 22);
      this.ctx.strokeStyle = '#3b82f6';
      this.ctx.strokeRect(padLeft + 4, padTop + 4, 340, 22);

      this.ctx.fillStyle = '#f8fafc';
      this.ctx.font = '11px monospace';
      this.ctx.textAlign = 'left';
      this.ctx.fillText(tipText, padLeft + 10, padTop + 19);
    }
  }
}

