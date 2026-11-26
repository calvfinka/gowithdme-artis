import test from "node:test";
import assert from "node:assert/strict";
await import("../src/artist-page.js");
const { status, daysUntil, label, split } = globalThis.GWM_Artist;
const L = { ended: "selesai", live: "Sedang berlangsung", today: "Hari ini", tmrw: "Besok", in: "H-{n}" };

test("status: mendatang, berlangsung, selesai (batas hari inklusif)", () => {
  assert.equal(status("2026-12-05", "2026-12-05", "2026-12-04"), "up");
  assert.equal(status("2026-12-05", "2026-12-05", "2026-12-05"), "live");   // hari-H masih berlangsung
  assert.equal(status("2026-12-05", "2026-12-05", "2026-12-06"), "ended");
  assert.equal(status("2026-11-01", "2026-11-30", "2026-11-25"), "live");   // festival multi-hari
  assert.equal(status("2026-11-01", "2026-11-30", "2026-11-30"), "live");
  assert.equal(status("2026-11-01", "2026-11-30", "2026-12-01"), "ended");
});
test("tanggal selesai kosong atau lebih awal dari mulai diperlakukan sama dengan mulai", () => {
  assert.equal(status("2026-12-05", "", "2026-12-05"), "live");
  assert.equal(status("2026-12-05", undefined, "2026-12-06"), "ended");
  assert.equal(status("2026-12-05", "2026-12-01", "2026-12-06"), "ended");
});
test("hitung mundur lintas bulan dan tahun", () => {
  assert.equal(daysUntil("2026-12-05", "2026-11-25"), 10);
  assert.equal(daysUntil("2027-01-02", "2026-12-30"), 3);
  assert.equal(daysUntil("2028-03-01", "2028-02-28"), 2);  // tahun kabisat
});
test("label: H-n, besok, hari ini, berlangsung, selesai", () => {
  assert.equal(label("up", "2026-12-05", "2026-11-25", L), "H-10");
  assert.equal(label("up", "2026-11-26", "2026-11-25", L), "Besok");
  assert.equal(label("up", "2026-11-25", "2026-11-25", L), "Hari ini");
  assert.equal(label("live", "2026-11-01", "2026-11-25", L), "Sedang berlangsung");
  assert.equal(label("ended", "2026-11-01", "2026-11-25", L), "selesai");
});
test("split: mendatang menaik, selesai menurun, event berlangsung ikut daftar mendatang di depan", () => {
  const items = [
    { s: "2026-12-20", e: "2026-12-20" }, { s: "2026-10-01", e: "2026-10-01" },
    { s: "2026-11-20", e: "2026-11-30" }, { s: "2026-12-05", e: "2026-12-05" }, { s: "2026-09-01", e: "2026-09-02" },
  ];
  const r = split(items, "2026-11-25");
  assert.deepEqual(r.cur.map(x => x.it.s), ["2026-11-20", "2026-12-05", "2026-12-20"]);
  assert.deepEqual(r.cur.map(x => x.st), ["live", "up", "up"]);
  assert.deepEqual(r.past.map(x => x.it.s), ["2026-10-01", "2026-09-01"]);
});
