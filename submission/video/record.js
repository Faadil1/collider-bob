// Records the real COLLIDER flow as a lossless-ish CDP screencast (1920x1080),
// plus an event log: timestamps, mouse targets and element rects (video px).
const { chromium } = require('playwright-core');
const fs = require('fs');
const OUT = process.env.REC_OUT || require('path').join(__dirname, 'rec');
fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT + '/frames', { recursive: true }); fs.mkdirSync(OUT + '/stills', { recursive: true });
const DSF = 2;          // stills are 3200x1800; screencast frames stay at CSS size
const VID = 1920 / 1600; // rects are logged in 1920x1080 video space

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome" });
  const ctx = await browser.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: DSF });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  const frames = []; let t0 = null; let n = 0;
  cdp.on('Page.screencastFrame', async (f) => {
    const ts = f.metadata.timestamp; if (t0 === null) t0 = ts;
    const file = `frames/${String(n++).padStart(6, '0')}.jpg`;
    fs.writeFileSync(`${OUT}/${file}`, Buffer.from(f.data, 'base64'));
    frames.push({ t: +(ts - t0).toFixed(4), file });
    cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  const events = [];
  const now = () => (t0 === null ? 0 : Date.now() / 1000 - t0);
  const mark = async (name, sels = {}) => {
    const rects = await page.evaluate((sels) => {
      const r = {};
      for (const [k, s] of Object.entries(sels)) {
        const el = document.querySelector(s); if (!el) continue;
        const b = el.getBoundingClientRect(); r[k] = [b.x, b.y, b.width, b.height];
      }
      return r;
    }, sels);
    for (const k of Object.keys(rects)) rects[k] = rects[k].map((v) => +(v * VID).toFixed(1));
    const ev = { t: +now().toFixed(3), name, rects };
    if (Object.keys(sels).length) { ev.still = `stills/${name.replace(':', '-')}.png`; await page.screenshot({ path: `${OUT}/${ev.still}` }); }
    events.push(ev); console.log('mark', name, now().toFixed(2));
  };
  let mouse = [800, 450];
  const moveTo = async (sel, name) => {
    const b = await page.locator(sel).first().boundingBox();
    const x = b.x + b.width / 2, y = b.y + b.height / 2;
    events.push({ t: +now().toFixed(3), name: 'move:' + name, from: mouse.map((v) => v * VID), to: [x * VID, y * VID], dur: 0.6 });
    await page.mouse.move(x, y, { steps: 18 }); mouse = [x, y];
  };
  const click = async (sel, name) => {
    await moveTo(sel, name); await page.waitForTimeout(250);
    events.push({ t: +now().toFixed(3), name: 'click:' + name, at: mouse.map((v) => v * VID) });
    await page.mouse.down(); await page.waitForTimeout(60); await page.mouse.up();
  };
  const hold = (ms) => page.waitForTimeout(ms);

  await page.goto(process.env.COLLIDER_URL || 'http://127.0.0.1:4173/');
  await page.waitForFunction(() => !document.getElementById('primary').disabled);
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: 1920, maxHeight: 1080, everyNthFrame: 1 });
  await hold(300);
  // Reload so DETECT's entrance animation is captured from its first frame.
  await page.reload(); await page.waitForFunction(() => !document.getElementById('primary').disabled);
  await mark('detect:start', {});
  await hold(1800);
  await mark('detect:settled', {
    tests: '.log-row:nth-child(1)', suites: '.log-row:nth-child(2)', but: '.log-but', conflicts: '.log-row.log-hit',
    chamber: '.chamber', hitA: '.chamber-h .hit-a', hitB: '.chamber-h .hit-b', notif: '.chamber-h .traj-notif',
    status: '#d-status', ledger: '.ledger-of-green',
  });
  await hold(3500);
  await click('#primary', 'run');
  await mark('decide:start', {});
  await hold(2000);
  await mark('decide:settled', {
    api: '.reading-api', ledgerR: '.reading-ledger', source: '.reading-source', plate: '.unknown-plate',
    word: '.up-word', foot: '.up-foot', drift: '.drift-strip', assume: '.assumption-strip', decision: '.decision',
    commit: '.decision-option.commit', keep: '.decision-option.keep-unknown', readings: '.readings',
  });
  await hold(3000);
  await moveTo('.decision-option.keep-unknown', 'keep'); await hold(1600);
  await click('.decision-option.commit', 'commit');
  await mark('compile:start', {});
  await page.waitForFunction(() => document.getElementById('primary').textContent.includes('Test future'), null, { timeout: 90000 });
  await mark('compile:ready', {});
  await hold(2600);
  await mark('compile:settled', {
    spine: '.spine', checklist: '#checklist', collapse: '.collapse', number: '#r-number', verdict: '#r-verdict',
    lanes: '#ws-mini', memory: '#memory-card', result: '#result',
  });
  await hold(2500);
  const guard = async (id, first) => {
    if (first) await click('#primary', 'guard-start'); else await click('#primary', 'guard-next-' + id);
    await mark(`guard${id}:start`, {});
    await page.waitForFunction(() => document.getElementById('phase-panel').dataset.phase === '1', null, { timeout: 90000 });
    await mark(`guard${id}:p1`, {});
    await page.waitForFunction(() => document.getElementById('phase-panel').dataset.phase === '2', null, { timeout: 30000 });
    await mark(`guard${id}:p2`, {
      docket: '#pr-list', card: '.change-card', conv: '.ci-conventional', sem: '.ci-semantic', verdict: '#p-verdict',
      count: '#p-ci-count', cf: '#p-cf', bench: '.bench', notes: '.bench-notes', memslab: '.memory-slab', inline: '#p-inline',
    });
    await page.waitForFunction(() => document.getElementById('phase-panel').dataset.phase === '4', null, { timeout: 30000 });
    await mark(`guard${id}:p4`, { band: '.restore-band' });
    await hold(2200);
  };
  await guard('A', true); await guard('B', false); await guard('C', false);
  await mark('replay:rail', { replay: '.rail-replay', rail: '#rail' });
  await hold(1500);
  await click('#secondary', 'proof');
  await hold(900);
  await click('#drawer-tabs [data-tab="Provenance"]', 'provenance');
  await hold(700);
  await mark('proof:provenance', { drawer: '#drawer', body: '#drawer-body' });
  // the separate LIVE_BOB section
  const sec = await page.evaluate(() => {
    const h = [...document.querySelectorAll('#drawer-body h3')].find((x) => x.textContent.startsWith('Separate LIVE_BOB'));
    const s = h.parentElement.getBoundingClientRect(); return [s.x, s.y, s.width, s.height];
  });
  events.push({ t: +now().toFixed(3), name: 'proof:bobsection', rects: { bob: sec.map((v) => +(v * VID).toFixed(1)) } });
  await hold(4500);
  await page.keyboard.press('Escape'); await hold(900);
  await click('.mode-switch [data-mode="EVIDENCE"]', 'evidence');
  await hold(700);
  await click('#explorer-nav [data-tab="Truth boundary"]', 'truth');
  await hold(600);
  await mark('evidence:truth', { body: '#explorer-body' });
  const sec2 = await page.evaluate(() => {
    const h = [...document.querySelectorAll('#explorer-body h3')].find((x) => x.textContent.startsWith('separate observed'));
    const s = h.parentElement.getBoundingClientRect(); return [s.x, s.y, s.width, s.height];
  });
  events.push({ t: +now().toFixed(3), name: 'evidence:bobsection', rects: { bob: sec2.map((v) => +(v * VID).toFixed(1)) } });
  await hold(4000);
  await click('.mode-switch [data-mode="ACTIVE"]', 'active');
  await hold(3500);
  await mark('end', {});
  await cdp.send('Page.stopScreencast');
  await hold(300);
  fs.writeFileSync(`${OUT}/frames.json`, JSON.stringify(frames));
  fs.writeFileSync(`${OUT}/events.json`, JSON.stringify(events, null, 1));
  console.log('frames', frames.length, 'duration', frames.at(-1).t);
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
