import { createElement } from '@/utils/dom';

export interface DrawerProps {
  title: string;
  onClose: () => void;
}

export class Drawer {
  private backdrop: HTMLElement;
  private panel: HTMLElement;
  private body: HTMLElement;

  constructor(private props: DrawerProps) {
    this.backdrop = createElement('div', { className: 'drawer-backdrop anim-fade-in' });
    this.panel = createElement('div', { className: 'drawer-panel' });

    const header = createElement('div', { className: 'drawer-header' });
    const title = createElement('h3', { text: props.title });
    const closeBtn = createElement('button', {
      className: 'btn btn-secondary btn-sm',
      text: '✕'
    });
    closeBtn.addEventListener('click', () => this.close());
    header.appendChild(title);
    header.appendChild(closeBtn);

    this.body = createElement('div', { className: 'drawer-body' });

    this.panel.appendChild(header);
    this.panel.appendChild(this.body);
    this.backdrop.appendChild(this.panel);

    this.backdrop.addEventListener('click', (e) => {
      if (e.target === this.backdrop) this.close();
    });
  }

  public setContent(element: HTMLElement | string): void {
    if (typeof element === 'string') {
      this.body.innerHTML = element;
    } else {
      this.body.innerHTML = '';
      this.body.appendChild(element);
    }
  }

  public open(): void {
    document.body.appendChild(this.backdrop);
  }

  public close(): void {
    if (this.backdrop.parentNode) {
      this.backdrop.parentNode.removeChild(this.backdrop);
    }
    this.props.onClose();
  }
}

