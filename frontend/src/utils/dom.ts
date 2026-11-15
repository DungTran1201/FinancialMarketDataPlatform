export function createElement<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  attrs: {
    className?: string;
    id?: string;
    text?: string;
    html?: string;
    style?: Partial<CSSStyleDeclaration>;
    attributes?: Record<string, string>;
  } = {}
): HTMLElementTagNameMap[K] {
  const el = document.createElement(tag);
  if (attrs.className) el.className = attrs.className;
  if (attrs.id) el.id = attrs.id;
  if (attrs.text !== undefined) el.textContent = attrs.text;
  if (attrs.html !== undefined) el.innerHTML = attrs.html;
  if (attrs.style) Object.assign(el.style, attrs.style);
  if (attrs.attributes) {
    for (const [k, v] of Object.entries(attrs.attributes)) {
      el.setAttribute(k, v);
    }
  }
  return el;
}

export function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

