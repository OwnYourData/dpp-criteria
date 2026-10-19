// Updates the cached copies in soya/context/ from their URLs.
//   node scripts/refresh_soya_context.js          fetch and write changed copies
//   node scripts/refresh_soya_context.js --check  only report copies that differ (exit 0)
// A copy is only replaced by a response that is 2xx JSON with "@context".
const fs = require('fs');
const path = require('path');
const { fetchContext } = require('./soya_context');

const CACHE = path.join(__dirname, '..', 'soya', 'context');
const INDEX = path.join(CACHE, 'index.json');

const main = async () => {
  const check = process.argv.includes('--check');
  const index = JSON.parse(fs.readFileSync(INDEX, 'utf8'));
  let failed = false;
  for (const [url, entry] of Object.entries(index)) {
    const file = path.join(CACHE, entry.file);
    const { text, problem } = await fetchContext(url);
    if (problem) {
      console.log(`${url}: ${problem}; cached copy from ${entry.fetched_at} kept`);
      failed = !check;
      continue;
    }
    const same = fs.existsSync(file) && fs.readFileSync(file, 'utf8') === text;
    if (check) {
      console.log(same ? `${url}: cached copy from ${entry.fetched_at} is current`
        : `::warning::${url} differs from the cached copy from ${entry.fetched_at}; run node scripts/refresh_soya_context.js`);
      continue;
    }
    if (!same) fs.writeFileSync(file, text);
    entry.fetched_at = new Date().toISOString().slice(0, 10);
    console.log(`${url}: ${same ? 'unchanged' : 'updated'}, fetched ${entry.fetched_at}`);
  }
  if (!check) fs.writeFileSync(INDEX, `${JSON.stringify(index, null, 2)}\n`);
  process.exit(failed ? 1 : 0);
};

main().catch((e) => { console.error(e); process.exit(1); });
