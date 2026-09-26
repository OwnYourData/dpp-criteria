// Validates the test vectors in tests/soya/<Structure>/<Criterion>/ through the
// SOyA web-cli: POST /acquire/<Structure>, then POST /validate/<Structure>.
//
//   valid/    no result for this criterion
//   warning/  at least one warning and no violation for this criterion
//   invalid/  at least one violation for this criterion
//
// Results belong to a criterion when their message starts with "[<criterion ID>]".
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const API = process.env.WEBCLI_URL || 'http://127.0.0.1:8080/api/v1';
const SH = 'http://www.w3.org/ns/shacl#';

const post = async (route, body) => {
  const res = await fetch(`${API}/${route}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${route}: HTTP ${res.status} ${await res.text()}`);
  return res.json();
};

const waitForWebCli = async () => {
  for (let i = 0; i < 60; i += 1) {
    try {
      if ((await fetch(`${API}/version`)).ok) return;
    } catch (e) { /* not up yet */ }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`web-cli not reachable at ${API}`);
};

const main = async () => {
  await waitForWebCli();
  let failures = 0;
  const base = path.join(ROOT, 'tests', 'soya');
  for (const structure of fs.readdirSync(base).sort()) {
    for (const criterion of fs.readdirSync(path.join(base, structure)).sort()) {
      for (const expected of ['valid', 'warning', 'invalid']) {
        const dir = path.join(base, structure, criterion, expected);
        if (!fs.existsSync(dir)) continue;
        for (const file of fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort()) {
          const passport = JSON.parse(fs.readFileSync(path.join(dir, file), 'utf8'));
          const data = await post(`validate/${structure}`, await post(`acquire/${structure}`, passport));
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
