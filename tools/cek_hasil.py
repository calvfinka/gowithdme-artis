# Pemeriksa hasil build: tautan lokal, canonical/hreflang, sitemap, sisa path lama. Keluar dengan kode 1 bila ada masalah.
# Jalankan setelah build:  python3 tools/cek_hasil.py   (dipakai juga oleh workflow sebelum commit)
import os,re,sys
from urllib.parse import urlparse,unquote
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
LANGS=("id","en")
def exists(path):
    p=os.path.join(ROOT,path.lstrip("/"))
    return os.path.isfile(p) or os.path.isfile(p+".html") or os.path.isfile(os.path.join(p,"index.html"))
pages=[]
for l in LANGS:
    for f in sorted(os.listdir(f"{ROOT}/{l}")):
        if f.endswith(".html"): pages.append(f"{l}/{f}")
pages+=["index.html","404.html"]
err=[]; nlinks=0
m=re.search(r'<link rel="canonical" href="(https?://[^/"]+)',open(f"{ROOT}/id/index.html",encoding="utf-8").read())
BASE=m.group(1) if m else ""
for pg in pages:
    s=open(f"{ROOT}/{pg}",encoding="utf-8").read()
    if "../../" in s: err.append(f"{pg}: sisa path '../../' dari struktur lama")
    if re.search(r'(?:href|src)="(?:\.\./)?a/',s): err.append(f"{pg}: sisa tautan ke a/")
    if "{{" in s or "@@" in s: err.append(f"{pg}: ada penanda yang belum diganti")
    d=os.path.dirname(pg)
    for kind,u in re.findall(r'<(?:a|link|script|img)\b[^>]*?\b(href|src)="([^"]*)"',s):
        if not u or u.startswith(("http:","https:","mailto:","data:","javascript:","#","//")): continue
        t=urlparse(u).path
        if not t: continue
        nlinks+=1
        full=os.path.normpath(os.path.join("/"+d,unquote(t))) if not t.startswith("/") else t
        if t.endswith("/"): full=full.rstrip("/")+"/"
        if full.endswith("/"): ok=exists(full+"index.html")
        else: ok=exists(full)
        if not ok: err.append(f"{pg}: tautan putus -> {u}")
    if pg not in ("404.html",):
        c=re.search(r'<link rel="canonical" href="([^"]+)"',s)
        if not c: err.append(f"{pg}: canonical tidak ada")
        elif BASE and not c.group(1).startswith(BASE): err.append(f"{pg}: canonical di luar {BASE}: {c.group(1)}")
        elif pg not in ("index.html",) :
            want=BASE+"/"+(pg[:-10] if pg.endswith("/index.html") else pg[:-5])
            if c.group(1)!=want: err.append(f"{pg}: canonical {c.group(1)} != {want}")
    for h in re.findall(r'hreflang="(?:id|en|x-default)" href="([^"]+)"',s):
        if BASE and h.startswith(BASE):
            p=h[len(BASE):] or "/"
            if not exists(p if not p.endswith("/") else p+"index.html"): err.append(f"{pg}: hreflang menuju halaman yang tidak ada -> {h}")
sm=open(f"{ROOT}/sitemap.xml",encoding="utf-8").read()
locs=re.findall(r"<loc>([^<]+)</loc>",sm)
for u in locs:
    p=u[len(BASE):] if BASE and u.startswith(BASE) else None
    if p is None: err.append(f"sitemap: {u} di luar {BASE}"); continue
    if not exists(p if not p.endswith("/") else p+"index.html"): err.append(f"sitemap: file tidak ada -> {u}")
if len(set(locs))!=len(locs): err.append("sitemap: ada URL ganda")
n_art=len(pages)-4  # dikurangi 2 indeks + index.html + 404.html
print(f"{len(pages)} halaman, {n_art//2} artis, {nlinks} tautan lokal, {len(locs)} URL sitemap")
if err:
    print(f"{len(err)} masalah:"); [print(" -",e) for e in err[:40]]; sys.exit(1)
print("OK: tidak ada masalah")
