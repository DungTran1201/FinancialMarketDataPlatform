import { createElement } from '@/utils/dom';

export interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md';
  onClick?: (e: MouseEvent) => void;
  icon?: string;
  disabled?: boolean;
}

export function createButton(props: ButtonProps): HTMLButtonElement {
  const btn = createElement('button', {
    className: `btn btn-${props.variant || 'secondary'} ${props.size === 'sm' ? 'btn-sm' : ''}`,
    text: props.label
  }) as HTMLButtonElement;

  if (props.disabled) {
    btn.disabled = true;
  }

  if (props.onClick) {
    btn.addEventListener('click', props.onClick);
  }

  return btn;
}

