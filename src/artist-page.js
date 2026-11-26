/* GoWithDME: halaman artis (/a/<nama>). Di-inline oleh tools/build.py ke setiap halaman artis (id dan en).
   Halaman dibangun statis, jadi status "mendatang / berlangsung / selesai" dihitung saat build dan bisa basi
   sampai sinkron berikutnya. Skrip ini menghitung ulang status memakai tanggal HARI INI di Jakarta (WIB):
   menggeser event yang sudah lewat ke "Event sebelumnya", memperbarui hitung mundur, ringkasan, dan angka.
   Tanpa JavaScript halaman tetap lengkap (HTML dari build). */
(function () {
  "use strict";

  /* ---- inti murni (diuji di tests/artist-page.test.mjs) ---- */
  function ms(d) { var p = d.split("-"); return Date.UTC(+p[0], +p[1] - 1, +p[2]); }
  /* s = tanggal mulai, e = tanggal selesai (YYYY-MM-DD), today = hari ini (YYYY-MM-DD) */
  function status(s, e, today) {
    if (!e || e < s) e = s;
    if (e < today) return "ended";
    if (s <= today) return "live";
    return "up";
  }
  function daysUntil(s, today) { return Math.round((ms(s) - ms(today)) / 864e5); }
  function label(st, s, today, L) {
    if (st === "ended") return L.ended;
    if (st === "live") return L.live;
    var n = daysUntil(s, today);
    if (n <= 0) return L.today;
    if (n === 1) return L.tmrw;
    return L["in"].replace("{n}", n);
  }
  /* pisahkan jadi {cur, past}: cur menaik menurut tanggal mulai, past menurun menurut tanggal selesai */
  function split(items, today) {
    var cur = [], past = [];
    items.forEach(function (it) {
      var st = status(it.s, it.e, today);
      (st === "ended" ? past : cur).push({ it: it, st: st });
    });
    cur.sort(function (a, b) { return a.it.s < b.it.s ? -1 : a.it.s > b.it.s ? 1 : 0; });
    past.sort(function (a, b) {
      var x = a.it.e || a.it.s, y = b.it.e || b.it.s;
      return x < y ? 1 : x > y ? -1 : (a.it.s < b.it.s ? 1 : a.it.s > b.it.s ? -1 : 0);
    });
    return { cur: cur, past: past };
  }
  var core = { status: status, daysUntil: daysUntil, label: label, split: split };
  if (typeof globalThis !== "undefined") globalThis.GWM_Artist = core;
  if (typeof document === "undefined") return;

  /* ---- bagian DOM ---- */
  var m = document.getElementById("m");
  if (!m) return;
  var today;
  try {
    today = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Jakarta", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  } catch (e) { return; }
  if (!/^\d{4}-\d\d-\d\d$/.test(today)) return;

  var d = m.dataset;
  var L = { ended: d.lEnded, live: d.lLive, today: d.lToday, tmrw: d.lTmrw, "in": d.lIn };
  var up = document.getElementById("up"), pa = document.getElementById("pa");
  if (!up || !pa) return;
  var lis = [].slice.call(m.querySelectorAll("li.ev[data-s]"));
  var byEl = [];
  var items = lis.map(function (li, i) { byEl[i] = li; return { i: i, s: li.dataset.s, e: li.dataset.e }; });
  var r = split(items, today);

  function paint(li, st, s) {
    li.setAttribute("data-st", st);
    var b = li.querySelector(".bd");
    if (b) { b.className = "bd st-" + st; b.textContent = label(st, s, today, L); }
    var tx = li.querySelector(".tx");
    if (tx) tx.hidden = st === "ended";
  }
  r.cur.forEach(function (x, k) {
    var li = byEl[x.it.i]; paint(li, x.st, x.it.s);
    li.classList.toggle("nx", k === 0);
    up.appendChild(li);
  });
  r.past.forEach(function (x) {
    var li = byEl[x.it.i]; paint(li, "ended", x.it.s);
    li.classList.remove("nx");
    pa.appendChild(li);
  });

  function $(id) { return document.getElementById(id); }
  function show(id, on) { var el = $(id); if (el) el.hidden = !on; }
  show("sec-up", r.cur.length > 0);
  show("sec-pa", r.past.length > 0);
  show("noup", r.cur.length === 0);
  var n1 = $("n-up"), n2 = $("n-pa");
  if (n1) n1.textContent = r.cur.length;
  if (n2) n2.textContent = r.past.length;

  var pill = $("pill"), lead = $("lead");
  if (r.cur.length) {
    var f = byEl[r.cur[0].it.i], st0 = r.cur[0].st;
    if (pill) { pill.className = "pill st-" + st0; pill.textContent = label(st0, r.cur[0].it.s, today, L); }
    if (lead) lead.textContent = d.lLead.replace("{t}", f.dataset.t).replace("{d}", f.dataset.fd);
  } else {
    if (pill) { pill.className = "pill st-none"; pill.textContent = d.lNone; }
    if (lead) lead.textContent = d.lNone2;
  }
})();
