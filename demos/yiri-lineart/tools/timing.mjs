// Dump the pen-tip speed (px/s, poster coords) at 100 Hz from the page → demos/yiri-lineart/timing.json (read by audio.py).
// Run from the repo root: MG_CHROME=<chromium> node demos/yiri-lineart/tools/timing.mjs
import http from 'node:http'; import fs from 'node:fs'; import path from 'node:path'; import { fileURLToPath } from 'node:url';
import puppeteer from 'puppeteer-core';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const srv = http.createServer((q, r) => {
  let p = path.join(ROOT, decodeURIComponent(new URL(q.url, 'http://x').pathname));
  if (!fs.existsSync(p)) { r.writeHead(404); return r.end(); }
  if (fs.statSync(p).isDirectory()) p = path.join(p, 'index.html');
  r.writeHead(200, { 'Content-Type': p.endsWith('.html') ? 'text/html' : p.endsWith('.json') ? 'application/json' : 'application/octet-stream' });
  fs.createReadStream(p).pipe(r);
}).listen(0, '127.0.0.1');
await new Promise((ok) => srv.on('listening', ok));
const b = await puppeteer.launch({ executablePath: process.env.MG_CHROME, args: ['--no-sandbox'] });
const pg = await b.newPage();
await pg.goto(`http://127.0.0.1:${srv.address().port}/demos/yiri-lineart/index.html`);
await pg.waitForFunction('window.__ready === true', { timeout: 120000 });
const speed = await pg.evaluate(() => Array.from({ length: 1001 }, (_, i) => +window.penSpeed(i / 100).toFixed(1)));
fs.writeFileSync(path.join(ROOT, 'demos/yiri-lineart/timing.json'), JSON.stringify({ hz: 100, speed }));
console.log('max speed', Math.max(...speed));
await b.close(); srv.close();
