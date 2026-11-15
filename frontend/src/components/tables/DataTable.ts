import { createElement } from '@/utils/dom';

export interface ColumnDef<T> {
  key: string;
  header: string;
  render?: (row: T) => HTMLElement | string;
  className?: string;
}

export interface DataTableProps<T> {
  columns: ColumnDef<T>[];
  data: T[];
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
}

export function createDataTable<T = any>(props: DataTableProps<T>): HTMLElement {
  const container = createElement('div', { className: 'table-container' });
  const table = createElement('table', { className: 'data-table' });

  // Header
  const thead = createElement('thead');
  const headerRow = createElement('tr');
  for (const col of props.columns) {
    const th = createElement('th', { text: col.header, className: col.className });
    headerRow.appendChild(th);
  }
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Body
  const tbody = createElement('tbody');
  if (props.data.length === 0) {
    const emptyRow = createElement('tr');
    const td = createElement('td', {
      text: props.emptyMessage || 'No records found',
      attributes: { colspan: String(props.columns.length) },
      style: { textAlign: 'center', padding: '24px' }
    });
    emptyRow.appendChild(td);
    tbody.appendChild(emptyRow);
  } else {
    for (const item of props.data) {
      const row = createElement('tr', {
        style: props.onRowClick ? { cursor: 'pointer' } : undefined
      });

      if (props.onRowClick) {
        row.addEventListener('click', () => props.onRowClick!(item));
      }

      for (const col of props.columns) {
        const td = createElement('td', { className: col.className });
        if (col.render) {
          const res = col.render(item);
          if (typeof res === 'string') {
            td.innerHTML = res;
          } else {
            td.appendChild(res);
          }
        } else {
          td.textContent = String((item as any)[col.key] ?? '—');
        }
        row.appendChild(td);
      }
      tbody.appendChild(row);
    }
  }

  table.appendChild(tbody);
  container.appendChild(table);
  return container;
}

