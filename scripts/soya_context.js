// Loads a JSON-LD context that a SOyA structure imports (for example
// https://ns.ownyourdata.eu/ns/soya-context.json) when the structures are built.
//
// The context is fetched from its URL. If that fails (no connection, timeout,
// a status other than 2xx, a response that is not JSON, or JSON without
// "@context"), the copy kept in soya/context/ is used instead. The result says
// which source was used and when the copy was fetched, so that tools built
// from it can tell their users. If there is no copy either, loading stops with
// a message that names the context.
const fs = require('fs');
const path = require('path');

const DEFAULT_TIMEOUT_MS = 15000;

const duration = (ms) => (ms < 1000 ? `${ms} ms` : `${Math.round(ms / 1000)} s`);

// Problem with a response, or null if it carries a JSON-LD context.
const responseProblem = (status, contentType, text) => {
  if (status < 200 || status > 299) return `HTTP ${status}`;
  if (!/json/i.test(contentType || '')) return `HTTP ${status} with ${contentType || 'no content type'} instead of JSON`;
  let json;
  try {
    json = JSON.parse(text);
  } catch (e) {
    return 'a response that is not valid JSON';
  }
  if (!json || typeof json['@context'] !== 'object') return 'JSON without "@context"';
  return null;
};

const fetchContext = async (url, { timeoutMs = DEFAULT_TIMEOUT_MS, fetchImpl = fetch } = {}) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetchImpl(url, { headers: { Accept: 'application/ld+json, application/json' }, signal: controller.signal });
    const text = await res.text();
    const problem = responseProblem(res.status, res.headers.get('content-type'), text);
    if (problem) return { problem };
    return { context: JSON.parse(text)['@context'], text };
  } catch (e) {
    if (controller.signal.aborted) return { problem: `no answer within ${duration(timeoutMs)}` };
    return { problem: `not reachable (${e.cause && e.cause.code ? e.cause.code : e.message})` };
  } finally {
    clearTimeout(timer);
  }
};

const readIndex = (cacheDir) => {
  const file = path.join(cacheDir, 'index.json');
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : {};
};

// Cached copy of the context at url, or null.
const cachedContext = (url, cacheDir) => {
  const entry = readIndex(cacheDir)[url];
  if (!entry) return null;
  const file = path.join(cacheDir, entry.file);
  if (!fs.existsSync(file)) return null;
  const json = JSON.parse(fs.readFileSync(file, 'utf8'));
  return { context: json['@context'], fetchedAt: entry.fetched_at };
};

// { context, stand } where stand = { url, source: "fetched" | "cached", fetched_at, reason? }.
const loadContext = async (url, { cacheDir, timeoutMs, fetchImpl, now = new Date() } = {}) => {
  const fetched = await fetchContext(url, { timeoutMs, fetchImpl });
  if (fetched.context) {
    return { context: fetched.context, stand: { url, source: 'fetched', fetched_at: now.toISOString().slice(0, 10) } };
  }
  const cached = cachedContext(url, cacheDir);
  if (!cached) {
    throw new Error(`SOyA context ${url} could not be retrieved (${fetched.problem}) and there is no cached copy in ${path.relative(process.cwd(), cacheDir) || cacheDir}`);
  }
  return { context: cached.context, stand: { url, source: 'cached', fetched_at: cached.fetchedAt, reason: fetched.problem } };
};

module.exports = { loadContext, fetchContext, cachedContext, responseProblem, DEFAULT_TIMEOUT_MS };
