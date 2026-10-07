import { test, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { request } from './api.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });
test('returns API data and carries mutation headers', async () => {
  globalThis.fetch = async (path, options) => {
    assert.equal(path, '/api/tasks');
    assert.equal(options.method, 'POST');
    assert.equal(options.headers['Content-Type'], 'application/json');
    return new Response(JSON.stringify({ id: 7 }), { status: 201 });
  };
  assert.deepEqual(await request('/api/tasks', { method: 'POST', body: '{}' }), { id: 7 });
});
test('successful delete does not attempt to parse an empty body', async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });
  assert.equal(await request('/api/tasks/7', { method: 'DELETE' }), null);
});
test('proxy failures produce useful text instead of a JSON parsing exception', async () => {
  globalThis.fetch = async () => new Response('<html>bad gateway</html>', { status: 502 });
  await assert.rejects(request('/api/tasks'), /temporarily unavailable/);
});
test('network failure gives a recovery action', async () => {
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(request('/api/tasks'), /Check your connection/);
});
test('validation and not-found errors stay understandable', async () => {
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: [{ msg: 'bad' }] }), { status: 422 });
  await assert.rejects(request('/api/tasks'), /Check the task details/);
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: 'Task not found' }), { status: 404 });
  await assert.rejects(request('/api/tasks/7'), /Task not found/);
});
