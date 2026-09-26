// Turns every SOyA structure in soya/*.yml into JSON-LD with `soya init` and
// embeds the imported SOyA context, so that validation needs no network access.
// Output: build/structures/<Name> (served as a local SOyA repository).
// Runs inside the oydeu/soya-web-cli image, which contains soya-js under /lib2.
const fs = require('fs');
const path = require('path');
const { Soya } = require(process.env.SOYA_JS || '/lib2/dist');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'build', 'structures');
const silent = { debug() {}, info() {}, warn() {}, error() {}, child() { return silent; } };

const main = async () => {
  const soya = new Soya({ logger: silent });
  fs.mkdirSync(OUT, { recursive: true });
  const contexts = {};
  for (const file of fs.readdirSync(path.join(ROOT, 'soya')).filter((f) => f.endsWith('.yml')).sort()) {
    const doc = await soya.init(fs.readFileSync(path.join(ROOT, 'soya', file), 'utf8'));
    const ctx = doc['@context'];
    const imported = ctx['@import'];
    if (imported) {
      if (!contexts[imported]) contexts[imported] = (await (await fetch(imported)).json())['@context'];
      delete ctx['@import'];
      doc['@context'] = { ...contexts[imported], ...ctx };
    }
    const name = path.basename(file, '.yml');
    fs.writeFileSync(path.join(OUT, name), JSON.stringify(doc));
    console.log(`built ${name}`);
  }
};

main().catch((e) => { console.error(e); process.exit(1); });
