// Turns every SOyA structure in soya/*.yml into JSON-LD with `soya init` and
// embeds the imported SOyA context, so that validation needs no network access.
// The context is fetched from its URL; if that fails, the copy in soya/context/
// is used (see scripts/soya_context.js).
// Output: build/structures/<Name> (served as a local SOyA repository) and
// build/soya-context.json (which context was used, fetched or cached, and from when).
// Runs inside the oydeu/soya-web-cli image, which contains soya-js under /lib2.
const fs = require('fs');
const path = require('path');
const { Soya } = require(process.env.SOYA_JS || '/lib2/dist');
const { loadContext } = require('./soya_context');

const ROOT = path.resolve(__dirname, '..');
const BUILD = process.env.BUILD_DIR ? path.resolve(process.env.BUILD_DIR) : path.join(ROOT, 'build');
const OUT = path.join(BUILD, 'structures');
const STAND = path.join(BUILD, 'soya-context.json');
const CACHE = path.join(ROOT, 'soya', 'context');
const silent = { debug() {}, info() {}, warn() {}, error() {}, child() { return silent; } };

const main = async () => {
  const soya = new Soya({ logger: silent });
  fs.mkdirSync(OUT, { recursive: true });
  const contexts = {};
  const stands = {};
  const structures = [];
  for (const file of fs.readdirSync(path.join(ROOT, 'soya')).filter((f) => f.endsWith('.yml')).sort()) {
    const doc = await soya.init(fs.readFileSync(path.join(ROOT, 'soya', file), 'utf8'));
    const ctx = doc['@context'];
    const imported = ctx['@import'];
    const name = path.basename(file, '.yml');
    if (imported) {
      if (!contexts[imported]) {
        const { context, stand } = await loadContext(imported, { cacheDir: CACHE });
        contexts[imported] = context;
        stands[imported] = stand;
        if (stand.source === 'cached') console.log(`${imported}: ${stand.reason}; using the cached copy from ${stand.fetched_at}`);
      }
      delete ctx['@import'];
      doc['@context'] = { ...contexts[imported], ...ctx };
    }
    fs.writeFileSync(path.join(OUT, name), JSON.stringify(doc));
    structures.push({ name, context: imported || null });
    console.log(`built ${name}`);
  }
  fs.writeFileSync(STAND, `${JSON.stringify({ built_at: new Date().toISOString(), structures, contexts: Object.values(stands) }, null, 2)}\n`);
};

main().catch((e) => { console.error(e); process.exit(1); });
