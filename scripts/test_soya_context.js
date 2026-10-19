// Tests for scripts/soya_context.js: node --test scripts/test_soya_context.js
const test = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const os = require('os');
const path = require('path');
const http = require('http');
const { loadContext } = require('./soya_context');

const CONTEXT = { '@context': { name: 'dct:title' } };
const CACHED = { '@context': { name: 'dct:title', cached: 'yes' } };

// HTTP server on 127.0.0.1 that answers with handler(req, res); returns { url, close }.
const serve = (handler) => new Promise((resolve) => {
  const sockets = new Set();
  const server = http.createServer(handler);
  server.on('connection', (s) => { sockets.add(s); s.on('close', () => sockets.delete(s)); });
  server.listen(0, '127.0.0.1', () => resolve({
    url: `http://127.0.0.1:${server.address().port}/ns/soya-context.json`,
    close: () => new Promise((done) => { sockets.forEach((s) => s.destroy()); server.close(done); })
  }));
});

const cacheFor = (url) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'soya-context-'));
  fs.writeFileSync(path.join(dir, 'soya-context.json'), JSON.stringify(CACHED));
  fs.writeFileSync(path.join(dir, 'index.json'), JSON.stringify({ [url]: { file: 'soya-context.json', fetched_at: '2026-10-01' } }));
  return dir;
};

const answer = (status, type, body) => (_req, res) => { res.writeHead(status, { 'Content-Type': type }); res.end(body); };

test('a reachable context is fetched and reported as fetched', async () => {
  const srv = await serve(answer(200, 'application/ld+json', JSON.stringify(CONTEXT)));
  try {
    const { context, stand } = await loadContext(srv.url, { cacheDir: cacheFor(srv.url), now: new Date('2026-10-19T10:00:00Z') });
    assert.deepStrictEqual(context, CONTEXT['@context']);
    assert.deepStrictEqual(stand, { url: srv.url, source: 'fetched', fetched_at: '2026-10-19' });
  } finally { await srv.close(); }
});

test('SOyA not reachable: the cached copy is used and the reason is reported', async () => {
  const srv = await serve(answer(200, 'application/json', '{}'));
  const { url } = srv;
  await srv.close();
  const { context, stand } = await loadContext(url, { cacheDir: cacheFor(url) });
  assert.deepStrictEqual(context, CACHED['@context']);
  assert.strictEqual(stand.source, 'cached');
  assert.strictEqual(stand.fetched_at, '2026-10-01');
  assert.match(stand.reason, /^not reachable/);
});

test('an HTML page instead of JSON is not parsed; the cached copy is used', async () => {
  const srv = await serve(answer(200, 'text/html', '<html> <head><title>Maintenance</title></head></html>'));
  try {
    const { context, stand } = await loadContext(srv.url, { cacheDir: cacheFor(srv.url) });
    assert.deepStrictEqual(context, CACHED['@context']);
    assert.strictEqual(stand.reason, 'HTTP 200 with text/html instead of JSON');
  } finally { await srv.close(); }
});

test('an HTML error page with status 502 is not parsed; the cached copy is used', async () => {
  const srv = await serve(answer(502, 'text/html', '<html> <head><title>502 Bad Gateway</title></head></html>'));
  try {
    const { stand } = await loadContext(srv.url, { cacheDir: cacheFor(srv.url) });
    assert.strictEqual(stand.source, 'cached');
    assert.strictEqual(stand.reason, 'HTTP 502');
  } finally { await srv.close(); }
});

test('JSON without @context is not taken as the context', async () => {
  const srv = await serve(answer(200, 'application/json', '{"error":"not found"}'));
  try {
    const { stand } = await loadContext(srv.url, { cacheDir: cacheFor(srv.url) });
    assert.strictEqual(stand.reason, 'JSON without "@context"');
  } finally { await srv.close(); }
});

test('a timeout falls back to the cached copy within the time limit', async () => {
  const srv = await serve(() => {});
  try {
    const started = Date.now();
    const { stand } = await loadContext(srv.url, { cacheDir: cacheFor(srv.url), timeoutMs: 300 });
    assert.ok(Date.now() - started < 3000, 'returned within the time limit');
    assert.strictEqual(stand.source, 'cached');
    assert.strictEqual(stand.reason, 'no answer within 300 ms');
  } finally { await srv.close(); }
});

test('without a cached copy loading stops with a clear message', async () => {
  const srv = await serve(answer(503, 'text/html', '<html> <h1>Service Unavailable</h1></html>'));
  try {
    const empty = fs.mkdtempSync(path.join(os.tmpdir(), 'soya-context-empty-'));
    await assert.rejects(loadContext(srv.url, { cacheDir: empty }),
      (e) => e.message.startsWith(`SOyA context ${srv.url} could not be retrieved (HTTP 503) and there is no cached copy`));
  } finally { await srv.close(); }
});
