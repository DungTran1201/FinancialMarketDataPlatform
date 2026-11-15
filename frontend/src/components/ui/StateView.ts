import { createElement } from '@/utils/dom';

export function createLoadingView(message = 'Loading data...'): HTMLElement {
  const container = createElement('div', { className: 'empty-state anim-fade-in' });
  const spinner = createElement('div', { className: 'loader-spinner' });
  const text = createElement('div', { className: 'loader-text', text: message });
  container.appendChild(spinner);
  container.appendChild(text);
  return container;
}

export function createEmptyView(title = 'No Data Available', subtitle = 'No records match the current filter criteria.'): HTMLElement {
  const container = createElement('div', { className: 'empty-state anim-fade-in' });
  const icon = createElement('div', { className: 'empty-state-icon', text: '📊' });
  const h3 = createElement('h3', { text: title });
  const p = createElement('p', { text: subtitle });
  container.appendChild(icon);
  container.appendChild(h3);
  container.appendChild(p);
  return container;
}

export function createErrorView(message = 'An unexpected error occurred.', onRetry?: () => void): HTMLElement {
  const container = createElement('div', { className: 'error-state anim-fade-in' });
  const icon = createElement('div', { className: 'error-state-icon', text: '⚠️' });
  const h3 = createElement('h3', { text: 'Connection / Query Error' });
  const p = createElement('p', { text: message });
  container.appendChild(icon);
  container.appendChild(h3);
  container.appendChild(p);

  if (onRetry) {
    const btn = createElement('button', {
      className: 'btn btn-primary',
      text: 'Retry Operation'
    });
    btn.addEventListener('click', onRetry);
    container.appendChild(btn);
  }

  return container;
}

