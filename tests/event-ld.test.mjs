import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { execSync } from "node:child_process";
// Memastikan setiap Event di JSON-LD halaman artis punya description, performer, dan offers (bila ada harga/tautan tiket).
function ld(file){const h=fs.readFileSync(file,"utf8");return [...h.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs)].map(m=>JSON.parse(m[1]));}
test("semua Event artis lengkap (description, performer, offers)", () => {
  let n=0;
  for (const l of ["id","en"]) for (const f of fs.readdirSync(l)) {
    if (!f.endsWith(".html") || f==="index.html") continue;
    for (const o of ld(`${l}/${f}`)) for (const e of (o.event||[])) {
      n++; assert.ok(e.description && e.description.length>20, `${l}/${f} description`);
      assert.ok(Array.isArray(e.performer)&&e.performer.length>0, `${l}/${f} performer`);
      if (e.offers) assert.ok(e.offers.url && e.offers.priceCurrency, `${l}/${f} offers`);
    }
  }
  assert.ok(n>50);
});
