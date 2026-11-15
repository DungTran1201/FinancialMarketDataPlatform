import { createElement } from '@/utils/dom';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

export function createBadge(label: string, variant: BadgeVariant = 'neutral'): HTMLElement {
  return createElement('span', {
    className: `badge badge-${variant}`,
    text: label
  });
}

