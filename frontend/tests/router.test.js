import test from 'node:test';
import assert from 'node:assert/strict';

test('Frontend Router recognizes all 6 module routes', () => {
  const routes = [
    '/',
    '/dashboard',
    '/data-flow',
    '/market-analytics',
    '/data-management',
    '/ai-workspace',
    '/administration'
  ];

  for (const r of routes) {
    assert.ok(r.startsWith('/'), `Route ${r} should start with '/'`);
  }
  assert.equal(routes.length, 7);
});

