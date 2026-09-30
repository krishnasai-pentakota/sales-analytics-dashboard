// Runs the dashboard's own JavaScript engine (taken straight from dashboard/index.html) on a fixed set
// of filter cases and prints the results as JSON. tests/test_kpis.py compares them with src/kpis.py.
//   node src/engine_reference.js > tests/fixtures/engine_reference.json
const fs = require('fs'), path = require('path'), vm = require('vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'dashboard', 'index.html'), 'utf8');
const payload = JSON.parse(html.match(/<script id="hist" type="application\/json">(.*?)<\/script>/s)[1].replace(/<\\\//g, '</'));
const code = html.match(/<script>\s*\/\* Sales engine[\s\S]*?<\/script>/)[0].replace(/^<script>|<\/script>$/g, '');
const sandbox = { module: { exports: {} }, console };
vm.runInNewContext(code + '\nmodule.exports = Engine;', sandbox);
const E = sandbox.module.exports;
const raw = E.decodePayload(payload);
raw.settings.reliable_from = '2025-04-01';   // same as the dashboard's HIST_COMPLETE_FROM
const M = E.build(raw);
const base = { cat: 'ALL', sub: 'ALL', cust: 'ALL', sp: 'ALL', scope: 'CUSTOMER', cmp: 'LY', ybasis: 1, grain: 'M' };
const cases = [
  { name: 'Sep 2026 all products', f: { ...base, period: Date.UTC(2026, 8, 1) } },
  { name: 'Aug 2026 all products', f: { ...base, period: Date.UTC(2026, 7, 1) } },
  { name: 'Jun 2026 all products', f: { ...base, period: Date.UTC(2026, 5, 1) } },
  { name: 'Aug 2026 ribbons', f: { ...base, cat: 'RIBBON', period: Date.UTC(2026, 7, 1) } },
  { name: 'Aug 2026 bows', f: { ...base, cat: 'BOW', period: Date.UTC(2026, 7, 1) } },
  { name: 'Aug 2026 largest customer', f: { ...base, cust: 'C:CUS001', period: Date.UTC(2026, 7, 1) } },
  { name: 'Jun 2026 incl. HQ / stock', f: { ...base, scope: 'ALL', period: Date.UTC(2026, 5, 1) } },
];
const out = cases.map(({ name, f }) => {
  const a = E.analyse(M, f);
  return { name, filter: f, net: a.cur.net, intake: a.cur.intake, book_to_bill: a.cur.b2b, otd: a.cur.otd, otd_lines: a.cur.otdN,
           open_value: a.openVal, open_lines: a.openLines, overdue_value: a.overdueVal, overdue_lines: a.overdueLines };
});
// the trend must follow the Compare choice: with 'previous period', each bar's comparison is the bar before it
const tr = E.analyse(M, { ...base, cmp: 'PREV', period: Date.UTC(2026, 8, 1) }).trend;
const prevTrend = { last_net: tr[tr.length - 1].net, last_comparison: tr[tr.length - 1].netLY, previous_bar_net: tr[tr.length - 2].net };
const season = E.seasonality(M, base).map(r => ({ y: r.y, m: r.m, net: r.net }));
process.stdout.write(JSON.stringify({ data_end: M.dataEnd, cases: out, prev_trend: prevTrend, season }, null, 1));
