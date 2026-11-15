import test from 'node:test';
import assert from 'node:assert/strict';

function formatPrice(val) {
  if (val === undefined || val === null || val === '') return '—';
  const num = typeof val === 'string' ? parseFloat(val) : val;
  if (isNaN(num)) return '—';
  return '$' + new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: num < 1 ? 6 : 2
  }).format(num);
}

function formatLatency(ms) {
  if (ms === undefined || ms === null || isNaN(ms)) return '— ms';
  if (ms < 1) return `${(ms * 1000).toFixed(0)} μs`;
  if (ms < 1000) return `${ms.toFixed(1)} ms`;
  return `${(ms / 1000).toFixed(2)} s`;
}

test('formatPrice correctly formats numbers and strings', () => {
  assert.equal(formatPrice(65432.1), '$65,432.10');
  assert.equal(formatPrice('100.5'), '$100.50');
  assert.equal(formatPrice(null), '—');
});

test('formatLatency handles sub-millisecond and seconds scaling', () => {
  assert.equal(formatLatency(0.2), '200 μs');
  assert.equal(formatLatency(15.4), '15.4 ms');
  assert.equal(formatLatency(1500), '1.50 s');
});

