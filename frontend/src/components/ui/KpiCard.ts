import { createElement } from '@/utils/dom';

export interface KpiCardProps {
  label: string;
  value: string;
  trend?: string;
  trendType?: 'positive' | 'negative' | 'neutral';
  subtitle?: string;
}

export function createKpiCard(props: KpiCardProps): HTMLElement {
  const card = createElement('div', { className: 'kpi-card' });

  const label = createElement('div', { className: 'kpi-label', text: props.label });
  const value = createElement('div', { className: 'kpi-value', text: props.value });

  card.appendChild(label);
  card.appendChild(value);

  if (props.trend) {
    const trend = createElement('div', {
      className: `kpi-trend ${props.trendType || 'neutral'}`,
      text: props.trend
    });
    card.appendChild(trend);
  }

  if (props.subtitle) {
    const sub = createElement('div', { className: 'card-subtitle', text: props.subtitle });
    card.appendChild(sub);
  }

  return card;
}

