// Validates the test vectors in tests/soya/<Structure>/<Criterion>/ against the
// SOyA structures in soya/, the same way `soya acquire <Structure> | soya validate
// <Structure>` does, but with the local structure instead of the published one.
//
//   valid/    no result for this criterion
//   warning/  at least one warning and no violation for this criterion
//   invalid/  at least one violation for this criterion
//
// Results belong to a criterion when their message starts with "[<criterion ID>]".
const fs = require('fs');
const path = require('path');
const { Soya, Overlays } = require('soya-js');
const { flat2ld } = require('soya-js/dist/system/flat2ld');

const ROOT = path.resolve(__dirname, '..');
const SH = 'http://www.w3.org/ns/shacl#';
const silent = { debug() {}, info() {}, warn() {}, error() {}, child() { return silent; } };

const main = async () => {
  const soya = new Soya({ logger: silent });
  let failures = 0;
  const base = path.join(ROOT, 'tests', 'soya');
  for (const structure of fs.readdirSync(base).sort()) {
    const yml = fs.readFileSync(path.join(ROOT, 'soya', `${structure}.yml`), 'utf8');
    const doc = await soya.init(yml);
    for (const criterion of fs.readdirSync(path.join(base, structure)).sort()) {
      for (const expected of ['valid', 'warning', 'invalid']) {
        const dir = path.join(base, structure, criterion, expected);
        if (!fs.existsSync(dir)) continue;
        for (const file of fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
          const passport = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
          const { data } = await new Overlays.SoyaValidate().run(doc, await flat2ld(passport, doc));
          const own = data.results
            .map((r) => ({ severity: r.severity.value, message: [].concat(r.message)[0]?.value ?? '' }))
            .filter((r) => r.message.startsWith(`[${criterion}]`));
          const violations = own.filter((r) => r.severity === `${SH}Violation`).length;
          const warnings = own.filter((r) => r.severity === `${SH}Warning`).length;
          const ok = data.classChecks.length === 0 && {
            valid: violations === 0 && warnings === 0,
            warning: violations === 0 && warnings > 0,
            invalid: violations > 0,
          }[expected];
          console.log(`${ok ? 'ok  ' : 'FAIL'} ${structure}/${criterion}/${expected}/${file}  (${violations} violations, ${warnings} warnings)`);
          if (!ok) {
            failures += 1;
            own.forEach((r) => console.log(`       ${r.severity.replace(SH, '')}: ${r.message}`));
            data.classChecks.forEach((c) => console.log(`       ${c.message}: ${c.name}`));
          }
        }
      }
    }
  }
  process.exit(failures ? 1 : 0);
};

main().catch((e) => { console.error(e); process.exit(2); });
