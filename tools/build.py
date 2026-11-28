# Bangun situs Direktori Artis (artis.gowithdme.com): data/events.json -> id/<artis>.html, en/<artis>.html,
# indeks id/ dan en/, pengalih bahasa di akar, 404.html, sitemap.xml, robots.txt.
# Dipindah dari tools/build.py repo utama (gowithdme). Jalankan:  python3 tools/gen_events.py && python3 tools/build.py
#
# PENTING: logika nama -> slug di bawah (split_lineup, _akey, _aslug, dan perulangan ARTISTS) HARUS sama persis dengan
# yang ada di tools/build.py repo utama, karena halaman event di repo utama menaut ke artis.gowithdme.com/<bahasa>/<slug>.
# Ubah di salah satu repo, ubah juga di repo satunya.
import os,re,json,time,html as _h
from datetime import date as _date, datetime as _dtm, timezone as _tzm, timedelta as _tdm
import unicodedata as _ud
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
# Alamat situs ini (canonical, hreflang, sitemap) dan situs utama (halaman event, poster, gambar pratinjau).
# Untuk uji lokal:  GWM_SITE=http://localhost:8000 python3 tools/build.py
BASE=os.environ.get("GWM_SITE","https://artis.gowithdme.com").rstrip("/")
MAIN=os.environ.get("GWM_MAIN","https://gowithdme.com").rstrip("/")
VER=os.environ.get("GWM_VER") or time.strftime("%Y%m%d%H%M")  # GWM_VER tetap -> build ulang tidak mengubah file (dipakai workflow)
LANGS=["id","en"]
# tanggal "hari ini" menurut WIB (UTC+7); build di server UTC tidak boleh salah hari antara 00:00-07:00 WIB
_NOW=os.environ.get("GWM_TODAY") or (_dtm.now(_tzm.utc)+_tdm(hours=7)).date().isoformat()
EV=[]
if os.path.exists(ROOT+"/data/events.json"):
    EV=[e for e in json.load(open(ROOT+"/data/events.json",encoding="utf-8")) if e.get("slug") and e.get("title") and e.get("event_date")]
CAT={"id":{"konser":"Konser","pameran":"Pameran","naikgunung":"Naik Gunung","festival":"Festival","komedi":"Komedi","seminar":"Seminar & Konferensi","meetup":"Meetup","lainnya":"Lainnya"},"en":{"konser":"Concert","pameran":"Exhibition","naikgunung":"Hiking","festival":"Festival","komedi":"Comedy","seminar":"Seminars & Conferences","meetup":"Meetup","lainnya":"Other"}}
TX={"id":{"note":"Cek ulang jadwal dan harga di kanal resmi penyelenggara sebelum membeli tiket."},
    "en":{"note":"Please re-check schedule and price on the organizer's official channel before buying tickets."}}
MON={"id":["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"],"en":["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]}
def fdate(l,d):
    y,m,dd=map(int,d[:10].split("-")); return f"{dd} {MON[l][m-1]} {y}"
def esc(x): return _h.escape(str(x),quote=True)
def ldj(o): return '<script type="application/ld+json">'+json.dumps(o,ensure_ascii=False).replace("</","<\\/")+'</script>'

TX["id"].update({"lineup_h":"Pengisi acara","a_title":"{a}: Jadwal Konser & Tiket","a_desc":"Jadwal konser dan festival {a}: {n} event di GoWithDME. {nx}","a_next":"Event terdekat: {t} pada {d}.","a_none":"Belum ada jadwal mendatang.","a_up":"Jadwal mendatang","a_past":"Event sebelumnya","a_qwhen":"Kapan {a} konser?","a_qnone":"Belum ada jadwal {a} yang akan datang di GoWithDME. Halaman ini diperbarui saat ada event baru.","a_all":"Semua artis","a_index_t":"Daftar Artis & Pengisi Acara","a_index_d":"Daftar artis dan pengisi acara konser dan festival di Indonesia beserta jadwalnya.","a_count":"{n} event","a_ended":"selesai"})
TX["en"].update({"lineup_h":"Line-up","a_title":"{a}: Concert Dates & Tickets","a_desc":"Concert and festival dates for {a}: {n} events on GoWithDME. {nx}","a_next":"Next show: {t} on {d}.","a_none":"No upcoming dates yet.","a_up":"Upcoming shows","a_past":"Past events","a_qwhen":"When is {a} playing next?","a_qnone":"There are no upcoming {a} dates on GoWithDME yet. This page is updated when new events are added.","a_all":"All artists","a_index_t":"Artists & Performers","a_index_d":"Artists and performers at concerts and festivals in Indonesia, with their dates.","a_count":"{n} events","a_ended":"ended"})
_PLACE=re.compile(r"menyusul|segera|soon|tba|tbc|tbd|lainnya|and more|to be announced|pengumuman|line-?up|musisi|guest star|masih banyak|^day\s*\d|^kategori\s|\b(januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember|january|february|march|june|july|august|october|december)\s+20\d\d",re.I)
def _akey(n): return re.sub(r"[^0-9a-z]+","",_ud.normalize("NFKD",n).encode("ascii","ignore").decode().lower() or n.lower()) or re.sub(r"\W+","",n.casefold())
def _aslug(n):
    a=_ud.normalize("NFKD",n).encode("ascii","ignore").decode().lower()
    return re.sub(r"[^0-9a-z]+","-",a).strip("-")
def split_lineup(txt):
    t=re.sub(r"\.\s*Day\s*\d+\s*\([^)]*\):\s*",", ",txt); t=re.sub(r"^\s*Day\s*\d+\s*\([^)]*\):\s*","",t)
    t=re.sub(r"\.\s+Dan masih.*$","",t,flags=re.I)
    out=[]
    for x in re.split(r"[,;\n]",t):
        x=re.sub(r"\([^)]*\)","",x).strip(" .\t\"'“”‘’"); x=re.sub(r"^Day\s*\d+\s*:\s*","",x,flags=re.I); x=re.sub(r"^(dan|and)\s+","",x,flags=re.I).strip(" .\"'")
        if re.fullmatch(r"day\s*\d+",x,re.I): continue
        if len(x)<2 or len(x)>60 or _PLACE.search(x): continue
        out.append(x)
    return out
ARTISTS={}   # key -> {"names":Counter,"events":[e..],"slug":...}
import collections as _col
for _e in EV:
    seen=set()
    for _n in split_lineup(_e.get("lineup") or ""):
        k=_akey(_n)
        if not k or k in seen: continue
        seen.add(k); a=ARTISTS.setdefault(k,{"names":_col.Counter(),"events":[]}); a["names"][_n]+=1; a["events"].append(_e)
_used=set()
for k,a in sorted(ARTISTS.items()):
    # nama tampilan = ejaan paling sering dipakai; seri: yang bukan huruf besar semua
    a["name"]=sorted(a["names"].items(),key=lambda kv:(-kv[1],kv[0].isupper(),kv[0]))[0][0]
    sl=_aslug(a["name"]) or k; base=sl; i=2
    while sl in _used: sl=f"{base}-{i}"; i+=1
    _used.add(sl); a["slug"]=sl
# ---- halaman artis: status event dihitung dari tanggal hari ini (WIB), bukan tanggal mesin build; JS (src/artist-page.js) menghitung ulang saat dibuka ----
TX["id"].update({"a_live":"Sedang berlangsung","a_today":"Hari ini","a_tmrw":"Besok","a_in":"H-{n}","a_nosched":"Belum ada jadwal","a_role":"Artis & pengisi acara","a_stat_total":"Total event","a_stat_up":"Mendatang","a_stat_city":"Kota","a_nx":"Penampilan berikutnya","a_ticket":"Tiket & info resmi","a_detail":"Lihat detail","a_pastn":"Event sebelumnya","a_with_h":"Sering satu line-up dengan","a_with_n":"{n}× bersama","a_faq_h":"Pertanyaan umum","a_upd":"Data diperbarui {d} (WIB)","a_lang":"English","a_home":"Beranda","a_f_where":"Di mana {a} akan tampil?","a_f_where_a":"{a} dijadwalkan tampil di {c}.","a_f_price":"Berapa harga tiket untuk menonton {a}?","a_f_price_a":"Untuk {t}: {p}.","a_f_count":"Berapa kali {a} tampil di GoWithDME?","a_f_count_a":"{a} tercatat di {n} event: {u} mendatang dan {p} sudah selesai.","a_f_with":"Siapa saja yang satu line-up dengan {a}?","a_f_with_a":"Nama yang paling sering tampil di event yang sama: {x}.","a_f_live_a":"{t} sedang berlangsung sampai {d}.","a_nx_range":"{a} – {b}"})
TX["en"].update({"a_live":"Happening now","a_today":"Today","a_tmrw":"Tomorrow","a_in":"In {n} days","a_nosched":"No dates yet","a_role":"Artist & performer","a_stat_total":"Total events","a_stat_up":"Upcoming","a_stat_city":"Cities","a_nx":"Next show","a_ticket":"Tickets & official info","a_detail":"View details","a_pastn":"Past events","a_with_h":"Often on the same bill as","a_with_n":"{n}× together","a_faq_h":"FAQ","a_upd":"Data updated {d} (WIB)","a_lang":"Bahasa Indonesia","a_home":"Home","a_f_where":"Where is {a} playing?","a_f_where_a":"{a} is scheduled to play in {c}.","a_f_price":"How much are tickets to see {a}?","a_f_price_a":"For {t}: {p}.","a_f_count":"How many shows does {a} have on GoWithDME?","a_f_count_a":"{a} appears in {n} events: {u} upcoming and {p} already finished.","a_f_with":"Who plays on the same bill as {a}?","a_f_with_a":"Names that most often share a line-up: {x}.","a_f_live_a":"{t} is happening now through {d}.","a_nx_range":"{a} – {b}"})
_NOSCHED=re.compile(r"menyusul|segera|soon|tba|tbc|tbd|info",re.I)
def _aend(x): return max((x.get("end_date") or x["event_date"])[:10],x["event_date"][:10])
def _ast(x,today=None):
    today=today or _NOW; s=x["event_date"][:10]; e=_aend(x)
    return "ended" if e<today else ("live" if s<=today else "up")
def _alabel(l,st,x):
    t=TX[l]
    if st=="ended": return t["a_ended"]
    if st=="live": return t["a_live"]
    n=(_date.fromisoformat(x["event_date"][:10])-_date.fromisoformat(_NOW)).days
    return t["a_today"] if n<=0 else (t["a_tmrw"] if n==1 else t["a_in"].format(n=n))
def _ainitials(nm):
    w=[x for x in re.split(r"[\s\-_.]+",nm) if re.search(r"[0-9A-Za-zÀ-￿]",x)]
    w=[re.sub(r"^[^0-9A-Za-zÀ-￿]+","",x) for x in w]
    s="".join(x[0] for x in w[:2]) if len(w)>1 else (w[0][:2] if w else "?")
    return s.upper()
def _atitle(l,x): return x.get("title_en") if l=="en" and x.get("title_en") else x["title"]
def _awhere(x):
    v=(x.get("venue") or "").strip(); c=(x.get("city") or "").strip()
    return ", ".join(p for p in (v,c) if p and not (p==c and v.lower().endswith(c.lower()))) 
def _aposter(x):
    pu=x.get("poster_url") or ""
    if not pu: return ""
    if re.match(r"https?://",pu): return pu
    return MAIN+"/"+pu.lstrip("/")  # poster lokal ada di repo utama (assets/posters/...)
def _aprice(x):
    p=(x.get("price_label") or "").strip()
    return "" if (not p or _NOSCHED.search(p)) else p
def _arange(l,x):
    sd=x["event_date"][:10]; ed=_aend(x)
    return fdate(l,sd)+((" – "+fdate(l,ed)) if ed!=sd else "")
# ---- data terstruktur Event: description, performer, offers terisi otomatis dari data event ----
_RP=re.compile(r"(?:Rp\.?\s*)(\d[\d.,]*)\s*(k|rb|ribu)?|(?:mulai(?:\s+dari)?)\s+(\d[\d.,]*)\s*(k|rb|ribu)?",re.I)
def _parse_prices(label):
    """'Mulai Rp100.000', 'Rp600.000 – Rp1.250.000', 'Rp1500K', 'Rp. 170,000' -> daftar angka rupiah. 'Gratis' -> [0]. Tidak jelas -> []."""
    p=(label or "").strip()
    if not p: return []
    out=[]
    for m in _RP.finditer(p):
        raw=m.group(1) or m.group(3); suf=(m.group(2) or m.group(4) or "").lower()
        n=int(re.sub(r"\D","",raw) or 0)
        if suf: n*=1000
        if n>=1000: out.append(n)
    if not out and re.match(r"\s*gratis",p,re.I): return [0]
    return out
def _aoffers(l,x,ended):
    pr=_parse_prices(x.get("price_label"))
    tu=x.get("ticket_url") or ""
    url=tu if re.match(r"https?://",tu) else f"{MAIN}/{l}/e/{x['slug']}"
    if not pr and not tu: return None
    o={"@type":"Offer","url":url,"priceCurrency":"IDR"}
    if not ended: o["availability"]="https://schema.org/InStock"
    if pr:
        lo,hi=min(pr),max(pr)
        if lo==hi: o["price"]=str(lo)
        else: o={"@type":"AggregateOffer","url":url,"priceCurrency":"IDR","lowPrice":str(lo),"highPrice":str(hi),**({"availability":o["availability"]} if "availability" in o else {})}
    return o
_DESC={"id":("{t} berlangsung di {w}, {r}.","Line-up: {p}.","Harga tiket: {h}."),"en":("{t} takes place at {w}, {r}.","Line-up: {p}.","Ticket price: {h}.")}
def _adesc(l,x,perf):
    d=_DESC[l]; w=_awhere(x) or "Indonesia"
    out=[d[0].format(t=_atitle(l,x),w=w,r=_arange(l,x))]
    if perf: out.append(d[1].format(p=", ".join(perf[:8])))
    h=_aprice(x)
    if h: out.append(d[2].format(h=h))
    return " ".join(out)
def _aperformers(x,aname):
    names=split_lineup(x.get("lineup") or "")[:12]
    if aname and _akey(aname) not in {_akey(n) for n in names}: names=[aname]+names
    return names
def _aevent_ld(l,x,aname=None):
    sd=x["event_date"][:10]; ed=_aend(x)
    perf=_aperformers(x,aname)
    o={"@type":"Event","name":_atitle(l,x),"description":_adesc(l,x,perf),"startDate":sd,"endDate":ed,"url":f"{MAIN}/{l}/e/{x['slug']}",
       "eventStatus":"https://schema.org/EventScheduled","eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode",
       "location":{"@type":"Place","name":x.get("venue") or x.get("city") or "Indonesia","address":{"@type":"PostalAddress","addressLocality":x.get("city") or "","addressCountry":"ID"}}}
    if perf: o["performer"]=[{"@type":"PerformingGroup","name":n} for n in perf]
    of=_aoffers(l,x,_ast(x)=="ended")
    if of: o["offers"]=of
    pu=x.get("poster_url") or ""
    if pu: o["image"]=[pu if re.match(r"https?://",pu) else MAIN+"/"+pu.lstrip("/")]
    return o
def _acompanions(a,limit=8):
    me=_akey(a["name"]); c=_col.Counter(); seen={}
    for x in a["events"]:
        for n in split_lineup(x.get("lineup") or ""):
            k=_akey(n)
            if k and k!=me and k in ARTISTS: c[k]+=1
    return [(ARTISTS[k],n) for k,n in sorted(c.items(),key=lambda kv:(-kv[1],ARTISTS[kv[0]]["name"].lower()))[:limit]]
def artist_page(l,a):
    o="en" if l=="id" else "id"; t=TX[l]; nm=a["name"]; u=f"{BASE}/{l}/{a['slug']}"
    evs=a["events"]
    cur=sorted([x for x in evs if _ast(x)!="ended"],key=lambda x:x["event_date"])
    pa=sorted([x for x in evs if _ast(x)=="ended"],key=lambda x:(_aend(x),x["event_date"]),reverse=True)
    nxe=cur[0] if cur else None
    nx=t["a_next"].format(t=_atitle(l,nxe),d=fdate(l,nxe["event_date"])) if nxe else t["a_none"]
    title=t["a_title"].format(a=nm); desc=t["a_desc"].format(a=nm,n=len(evs),nx=nx)
    cities=_col.Counter((x.get("city") or "").strip() for x in evs if (x.get("city") or "").strip())
    cats=[]
    for x in evs:
        c=CAT[l].get(x.get("category"),"")
        if c and c not in cats: cats.append(c)
    comp=_acompanions(a)
    # ---- kartu event ----
    def card(x):
        st=_ast(x); tt=_atitle(l,x); sd=x["event_date"][:10]; w=_awhere(x); pr=_aprice(x); img=_aposter(x)
        d_=int(sd[8:10]); mo=MON[l][int(sd[5:7])-1]
        th=(f'<a class="th" href="{MAIN}/{l}/e/{esc(x["slug"])}" tabindex="-1" aria-hidden="true"><img src="{esc(img)}" alt="" loading="lazy" decoding="async" width="108" height="144" onerror="this.parentNode.className=\'th dt\';this.parentNode.innerHTML=\'<b>{d_}</b><i>{mo}</i>\'"></a>' if img
            else f'<a class="th dt" href="{MAIN}/{l}/e/{esc(x["slug"])}" tabindex="-1" aria-hidden="true"><b>{d_}</b><i>{mo}</i></a>')
        cat=CAT[l].get(x.get("category"),"")
        tix=(f'<a class="bt tx" href="{esc(x["ticket_url"])}" rel="noopener nofollow" target="_blank"{" hidden" if st=="ended" else ""}>{esc(t["a_ticket"])}</a>') if x.get("ticket_url") else ""
        return (f'<li class="ev" data-s="{sd}" data-e="{_aend(x)}" data-t="{esc(tt)}" data-fd="{esc(fdate(l,sd))}" data-st="{st}" data-nx="{esc(t["a_nx"])}">{th}<div class="bo">'
            f'<div class="ln"><span class="bd st-{st}">{esc(_alabel(l,st,x))}</span>{f"<span class=ct>{esc(cat)}</span>" if cat else ""}</div>'
            f'<h3><a href="{MAIN}/{l}/e/{esc(x["slug"])}">{esc(tt)}</a></h3>'
            f'<p class="mt"><time datetime="{sd}">{esc(_arange(l,x))}</time>{(" · "+esc(w)) if w else ""}</p>'
            f'{f"<p class=pr>{esc(pr)}</p>" if pr else ""}'
            f'<div class="ac"><a class="bt pri" href="{MAIN}/{l}/e/{esc(x["slug"])}">{t["a_detail"]}</a>{tix}</div></div></li>')
    def cards(xs): return "".join(map(card,xs))
    # kedua daftar selalu ada di HTML (JS memindahkan kartu di antaranya); yang kosong disembunyikan
    nxs=[card(x) for x in cur]
    if nxs: nxs[0]=nxs[0].replace('<li class="ev"','<li class="ev nx"',1)
    up_h=f'<section class="sec" id="sec-up"{"" if cur else " hidden"}><h2>{t["a_up"]} <em id="n-up">{len(cur)}</em></h2><ul class="evl" id="up">{"".join(nxs)}</ul></section>'
    noup=f'<p class="noup" id="noup"{" hidden" if cur else ""}>{esc(t["a_qnone"].format(a=nm))}</p>'
    pa_h=f'<section class="sec" id="sec-pa"{"" if pa else " hidden"}><details class="more"{" open" if not cur else ""}><summary>{t["a_past"]} <em id="n-pa">{len(pa)}</em></summary><ul class="evl" id="pa">{cards(pa)}</ul></details></section>'
    # ---- hero ----
    stx=_ast(nxe) if nxe else "none"
    pill=_alabel(l,stx,nxe) if nxe else t["a_nosched"]
    chips="".join(f'<span class="chip">{esc(c)}</span>' for c in cats[:3])
    top_c=[c for c,_ in cities.most_common(4)]
    chips+="".join(f'<span class="chip">{esc(c)}</span>' for c in top_c)+(f'<span class="chip">+{len(cities)-4}</span>' if len(cities)>4 else "")
    hue=sum(map(ord,a["slug"]))%360
    hero=(f'<section class="hero"><div class="av" style="--h:{hue}" aria-hidden="true">{esc(_ainitials(nm))}</div>'
          f'<div><p class="eyebrow">{esc(t["a_role"])}</p><h1>{esc(nm)}</h1></div>'
          f'<span class="pill st-{stx}" id="pill">{esc(pill)}</span>'
          f'<p class="lead" id="lead">{esc(nx)}</p>'
          f'{f"<div class=meta>{chips}</div>" if chips else ""}</section>')
    stats=(f'<dl class="stats"><div class="stat"><dd>{len(evs)}</dd><dt>{t["a_stat_total"]}</dt></div>'
           f'<div class="stat"><dd id="st-up">{len(cur)}</dd><dt>{t["a_stat_up"]}</dt></div>'
           f'<div class="stat"><dd>{len(cities)}</dd><dt>{t["a_stat_city"]}</dt></div></dl>')
    withh=(f'<section class="sec"><h2>{t["a_with_h"]} {esc(nm)}</h2><div class="with">'+"".join(f'<a href="{esc(b["slug"])}">{esc(b["name"])} <small>{t["a_with_n"].format(n=n)}</small></a>' for b,n in comp)+'</div></section>') if comp else ""
    # ---- FAQ: hanya pertanyaan yang jawabannya benar-benar ada di data ----
    qa=[(t["a_qwhen"].format(a=nm),(t["a_f_live_a"].format(t=_atitle(l,nxe),d=fdate(l,_aend(nxe))) if (nxe and _ast(nxe)=="live") else (nx if cur else t["a_qnone"].format(a=nm))))]
    ucity=[]
    for x in cur:
        c=(x.get("city") or "").strip()
        if c and c not in ucity: ucity.append(c)
    if ucity: qa.append((t["a_f_where"].format(a=nm),t["a_f_where_a"].format(a=nm,c=", ".join(ucity[:4])+(f" +{len(ucity)-4}" if len(ucity)>4 else ""))))
    pe=next((x for x in cur if _aprice(x)),None)
    if pe: qa.append((t["a_f_price"].format(a=nm),t["a_f_price_a"].format(t=_atitle(l,pe),p=_aprice(pe))))
    qa.append((t["a_f_count"].format(a=nm),t["a_f_count_a"].format(a=nm,n=len(evs),u=len(cur),p=len(pa))))
    if comp: qa.append((t["a_f_with"].format(a=nm),t["a_f_with_a"].format(x=", ".join(b["name"] for b,_ in comp[:5]))))
    faq=f'<section class="sec"><h2>{t["a_faq_h"]}</h2><div class="faq">'+"".join(f'<details{" open" if i==0 else ""}><summary>{esc(q)}</summary><p>{esc(ans)}</p></details>' for i,(q,ans) in enumerate(qa))+"</div></section>"
    # ---- data terstruktur ----
    ld={"@context":"https://schema.org","@type":"PerformingGroup","name":nm,"url":u,"inLanguage":l,"event":[_aevent_ld(l,x,nm) for x in (cur+pa)[:12]]}
    bc={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"GoWithDME","item":f"{MAIN}/{l}/"},
        {"@type":"ListItem","position":2,"name":t["a_all"],"item":f"{BASE}/{l}/"},
        {"@type":"ListItem","position":3,"name":nm,"item":u}]}
    fld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in qa]}
    ogd=desc[:200]; ogi=f"{MAIN}/assets/og-image{'' if l=='id' else '-en'}.png"
    data=" ".join(f'data-{k}="{esc(v)}"' for k,v in (("l-ended",t["a_ended"]),("l-live",t["a_live"]),("l-today",t["a_today"]),("l-tmrw",t["a_tmrw"]),("l-in",t["a_in"]),("l-none",t["a_nosched"]),("l-lead",t["a_next"]),("l-none2",t["a_none"])))
    return f"""<!DOCTYPE html>
<html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} | GoWithDME</title><meta name="description" content="{esc(desc[:300])}">
<link rel="canonical" href="{u}"><link rel="alternate" hreflang="{l}" href="{u}"><link rel="alternate" hreflang="{o}" href="{BASE}/{o}/{a['slug']}"><link rel="alternate" hreflang="x-default" href="{BASE}/id/{a['slug']}">
<meta property="og:type" content="website"><meta property="og:site_name" content="GoWithDME"><meta property="og:locale" content="{"id_ID" if l=="id" else "en_US"}"><meta property="og:url" content="{u}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(ogd)}"><meta property="og:image" content="{ogi}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(ogd)}">
<meta name="theme-color" content="#0E5A46"><link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<script src="../js/theme.js?v={VER}"></script>
<style>{ART_CSS}{HDR_CSS}</style>{ldj(ld)}{ldj(bc)}{ldj(fld)}</head><body>
{site_bar(l,f'<a class="lang" href="../{o}/{esc(a["slug"])}" hreflang="{o}" lang="{o}">{t["a_lang"]}</a>')}
<div class="top"><nav class="crumb" aria-label="Breadcrumb"><a href="./">{t["a_all"]}</a><span aria-hidden="true">›</span><span aria-current="page">{esc(nm)}</span></nav></div>
<main id="m" {data}>
{hero}{stats}{up_h}{noup}{pa_h}{withh}{faq}
<footer class="foot"><p>{t["note"]}</p><p>{t["a_upd"].format(d=fdate(l,_NOW))} · <a href="./">{t["a_all"]}</a></p></footer>
</main><script>{ART_JS}</script></body></html>
"""
# ---- indeks artis (/<bahasa>/): grid kartu + cari, filter huruf, urutan. CSS/JS ada di src/artists-index.css dan .js, di-inline ke halaman ini saja (CSS global tidak tersentuh) ----
TX["id"].update({"a_count1":"{n} event","a_search":"Cari artis...","a_search_l":"Cari artis","a_trend_h":"Artis Trending","a_trend_d":"Nama yang paling sering muncul di line-up.","a_sort":"Urutkan","a_sort_e":"Event Terbanyak","a_sort_a":"A-Z","a_letter":"Filter berdasarkan huruf","a_all_l":"Semua","a_view":"Lihat Event","a_view_l":"Lihat event {a}","a_noup":"Belum ada jadwal mendatang","a_found1":"1 artis","a_foundn":"{n} artis","a_empty":"Tidak ada artis yang cocok.","a_reset":"Hapus filter","a_intro":"{n} artis dan pengisi acara konser dan festival di seluruh Indonesia."})
TX["en"].update({"a_count1":"{n} event","a_search":"Search artist...","a_search_l":"Search artists","a_trend_h":"Trending Artists","a_trend_d":"The names in the most line-ups.","a_sort":"Sort","a_sort_e":"Most Events","a_sort_a":"A-Z","a_letter":"Filter by letter","a_all_l":"All","a_view":"View Events","a_view_l":"View events for {a}","a_noup":"No upcoming dates yet","a_found1":"1 artist","a_foundn":"{n} artists","a_empty":"No artists match your search.","a_reset":"Clear filters","a_intro":"{n} artists and performers from concerts and festivals across Indonesia."})
def _read_src(n): return open(f"{ROOT}/src/{n}",encoding="utf-8").read().strip()
LOGO_MARK='<svg class="mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><rect class="mk-bg" width="32" height="32" rx="7.5"/><path class="mk-g" d="M23.35 11.75A8.5 8.5 0 1 0 24.5 16"/><path class="mk-b" d="M16.5 16H24.5"/></svg>'
LOGO_WORD='<span class="w">GoWith<b>DME</b></span>'
def site_bar(l,right=""): return f'<header class="gb"><div class="gb-in"><a class="logo" href="{MAIN}/{l}/" aria-label="GoWithDME">{LOGO_MARK}{LOGO_WORD}</a><span class="sp"></span>{right}</div></header>'

def _aletter(n):
    m=re.search(r"[A-Z0-9]",_ud.normalize("NFKD",n).encode("ascii","ignore").decode().upper())
    return m.group() if m and m.group().isalpha() else "#"
def _axcard(l,a,rank=0,dup=False):
    # rank>0: kartu Trending (besar). dup: salinan Trending di grid utama (disembunyikan CSS saat tampilan awal).
    t=TX[l]; n=len(a["events"]); nm=esc(a["name"]); sl=esc(a["slug"])
    up=sorted([x for x in a["events"] if (x.get("end_date") or x["event_date"])[:10]>=_NOW],key=lambda x:x["event_date"])[:2]
    def row(x):
        tt=x.get("title_en") if l=="en" and x.get("title_en") else x["title"]
        c=(esc(x["city"])+", ") if x.get("city") else ""
        return f'<li><a href="{MAIN}/{l}/e/{esc(x["slug"])}">{esc(tt)}</a><span>{c}<time datetime="{esc(x["event_date"][:10])}">{esc(fdate(l,x["event_date"]))}</time></span></li>'
    evs=f'<ul class="ax-ev">{"".join(map(row,up))}</ul>' if up else f'<p class="ax-ev ax-no">{t["a_noup"]}</p>'
    btn=f'<a class="ax-b" href="{sl}" aria-label="{esc(t["a_view_l"].format(a=a["name"]))}">{t["a_view"]}</a>'
    name=f'<h3 class="ax-n"><a href="{sl}">{nm}</a></h3>'
    if rank:
        k=f'<p class="ax-k"><b>{n}</b> {t["a_count"].format(n="").strip()}</p>'
        return f'<li class="ax-t"><div class="ax-top"><span class="ax-rk">#{rank}</span>{k}</div>{name}{evs}{btn}</li>'
    k=f'<p class="ax-k">{(t["a_count1"] if n==1 else t["a_count"]).format(n=n)}</p>'
    return f'<li class="ax-c" data-l="{_aletter(a["name"])}"{" data-t" if dup else ""}>{name}{k}{evs}{btn}</li>'
def artist_index(l):
    o="en" if l=="id" else "id"; t=TX[l]; u=f"{BASE}/{l}/"
    items=sorted(ARTISTS.values(),key=lambda a:(-len(a["events"]),a["name"].lower()))
    letters=sorted({_aletter(a["name"]) for a in items},key=lambda c:(c!="#",c))
    trend="".join(_axcard(l,a,i+1) for i,a in enumerate(items[:3]))
    cards="".join(_axcard(l,a,0,i<3) for i,a in enumerate(items))
    chips=f'<button type="button" data-l="" aria-pressed="true">{t["a_all_l"]}</button>'+"".join(f'<button type="button" data-l="{c}" aria-pressed="false">{c}</button>' for c in letters)
    return f"""<!DOCTYPE html>
<html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t["a_index_t"]} | GoWithDME</title><meta name="description" content="{esc(t["a_index_d"])}">
<link rel="canonical" href="{u}"><link rel="alternate" hreflang="{l}" href="{u}"><link rel="alternate" hreflang="{o}" href="{BASE}/{o}/"><link rel="alternate" hreflang="x-default" href="{BASE}/id/">
<meta name="theme-color" content="#0E5A46"><link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<script src="../js/theme.js?v={VER}"></script>
<style>{_read_src("artists-index.css")}{HDR_CSS}</style><noscript><style>.ax-tools{{display:none}}</style></noscript></head>
<body>{site_bar(l)}<div class="ax ax-def" id="ax" data-f1="{esc(t["a_found1"])}" data-fn="{esc(t["a_foundn"])}">
<h1>{t["a_index_t"]}</h1><p class="ax-intro">{t["a_intro"].format(n=len(items))}</p>
<div class="ax-tools"><div class="ax-row">
<label class="ax-search"><span class="ax-sr">{t["a_search_l"]}</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><input id="ax-q" type="search" placeholder="{esc(t["a_search"])}" autocomplete="off" spellcheck="false" enterkeyhint="search"></label>
<div class="ax-sort" role="group" aria-label="{t["a_sort"]}"><button type="button" data-s="e" aria-pressed="true">{t["a_sort_e"]}</button><button type="button" data-s="a" aria-pressed="false">{t["a_sort_a"]}</button></div>
</div><div class="ax-az" role="group" aria-label="{t["a_letter"]}">{chips}</div></div>
<section class="ax-trend" aria-labelledby="ax-th"><div class="ax-h"><h2 id="ax-th">{t["a_trend_h"]}</h2><p>{t["a_trend_d"]}</p></div><ul class="ax-tr">{trend}</ul></section>
<section aria-labelledby="ax-ah"><div class="ax-h"><h2 id="ax-ah">{t["a_all"]}</h2><p id="ax-count" aria-live="polite">{t["a_foundn"].format(n=len(items)-3)}</p></div>
<ul class="ax-grid">{cards}</ul>
<div class="ax-empty" id="ax-empty" hidden><p>{t["a_empty"]}</p><button type="button" id="ax-reset">{t["a_reset"]}</button></div></section>
</div><script>{_read_src("artists-index.js")}</script></body></html>
"""
assert "index" not in _used,"ada artis bernama 'Index': slugnya bentrok dengan index.html. Ganti nama di data event atau beri pengecualian di kedua repo."
HDR_CSS=_read_src("site-header.css"); ART_CSS=_read_src("artist-page.css"); ART_JS=_read_src("artist-page.js")

# ---- tulis halaman ----
def _w(p,s):
    with open(p,"w",encoding="utf-8") as f: f.write(s)
for l in LANGS:
    d=f"{ROOT}/{l}"; os.makedirs(d,exist_ok=True)
    for f in os.listdir(d):
        if f.endswith(".html"): os.remove(f"{d}/{f}")
    for a in ARTISTS.values(): _w(f"{d}/{a['slug']}.html",artist_page(l,a))
    _w(f"{d}/index.html",artist_index(l))

# ---- akar situs: pilih bahasa dari bahasa peramban (localStorage tidak terbagi antar-subdomain) ----
_CSS=("*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;background:#f5f5f7;color:#1d1d1f;"
 "font:16px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}main{max-width:440px;text-align:center}h1{margin:0 0 10px;font-size:22px;line-height:1.3}"
 "p{margin:0 0 24px;color:#6e6e73;font-size:15px}nav{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}"
 "a{padding:12px 22px;border-radius:12px;border:1px solid #0e5a46;color:#0e5a46;text-decoration:none;font-weight:600;font-size:15px}"
 "a.pri{background:#0e5a46;color:#fff}a:focus-visible{outline:3px solid #34d399;outline-offset:2px}"
 "@media(prefers-color-scheme:dark){body{background:#111113;color:#f5f5f7}p{color:#a1a1a6}a{border-color:#4fc9a4;color:#4fc9a4}a.pri{background:#4fc9a4;color:#062a20}}")
_T=TX_ROOT={"id":("Daftar Artis & Pengisi Acara","Daftar artis dan pengisi acara konser dan festival di Indonesia beserta jadwalnya."),
            "en":("Artists & Performers","Artists and performers at concerts and festivals in Indonesia, with their dates.")}
_w(ROOT+"/index.html",f'''<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0E5A46">
<title>{esc(_T["id"][0])} | GoWithDME</title><meta name="description" content="{esc(_T["id"][1])}">
<link rel="canonical" href="{BASE}/id/"><link rel="alternate" hreflang="id" href="{BASE}/id/"><link rel="alternate" hreflang="en" href="{BASE}/en/"><link rel="alternate" hreflang="x-default" href="{BASE}/id/">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><style>{_CSS}</style>
<noscript><meta http-equiv="refresh" content="0;url=id/"></noscript>
<script>(function(){{var l=/^id/i.test(navigator.language||"")?"id":"en";location.replace(l+"/"+location.search+location.hash)}})()</script></head>
<body><main><h1>{esc(_T["id"][0])}</h1><p>{esc(_T["id"][1])}</p><nav><a class="pri" href="id/">Bahasa Indonesia</a><a href="en/">English</a></nav></main></body></html>
''')

# ---- 404.html (GitHub Pages memakainya untuk alamat yang tidak ada; artis baru muncul setelah sinkron berikutnya) ----
_w(ROOT+"/404.html",f'''<!DOCTYPE html><html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><meta name="theme-color" content="#0E5A46">
<title>404 | GoWithDME</title><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><style>{_CSS}</style></head>
<body><main><h1 id="h">Halaman artis tidak ditemukan</h1><p id="p">Artis ini belum ada di daftar, atau alamatnya sudah berubah. Halaman artis baru muncul beberapa menit setelah event dengan line-up-nya terbit.</p>
<nav><a class="pri" id="a1" href="/id/">Semua artis</a><a href="{MAIN}/id/">GoWithDME</a></nav></main>
<script>(function(){{if(/^\\/en(\\/|$)/.test(location.pathname)||(!/^\\/id(\\/|$)/.test(location.pathname)&&!/^id/i.test(navigator.language||""))){{
document.documentElement.lang="en";document.getElementById("h").textContent="Artist page not found";
document.getElementById("p").textContent="This artist is not listed yet, or the address has changed. Artist pages appear a few minutes after an event with their line-up is published.";
var a=document.getElementById("a1");a.textContent="All artists";a.href="/en/"}}}})()</script></body></html>
''')

# ---- sitemap.xml dan robots.txt ----
_OLD=(_date.fromisoformat(_NOW)-_tdm(days=30)).isoformat()  # artis yang semua eventnya berakhir >30 hari lalu: halaman tetap ada, tapi keluar dari sitemap
_lms=[(x.get("created_at") or x["event_date"])[:10] for x in EV]
rows=[]
for l in LANGS:
    alt="".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{BASE}/{x}/"/>' for x in LANGS)
    rows.append(f"<url><loc>{BASE}/{l}/</loc>"+(f"<lastmod>{max(_lms)}</lastmod>" if _lms else "")+f"{alt}</url>")
for a in ARTISTS.values():
    if all((x.get("end_date") or x["event_date"])[:10]<_OLD for x in a["events"]): continue
    alt="".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{BASE}/{x}/{a["slug"]}"/>' for x in LANGS)
    lm=max((x.get("created_at") or x["event_date"])[:10] for x in a["events"])
    for l in LANGS: rows.append(f"<url><loc>{BASE}/{l}/{a['slug']}</loc><lastmod>{lm}</lastmod>{alt}</url>")
_w(ROOT+"/sitemap.xml",'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'+"".join(rows)+"</urlset>\n")
_w(ROOT+"/robots.txt",f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
print("selesai ->",BASE,"|",len(EV),"event,",len(ARTISTS),"artis,",len(rows),"URL di sitemap")
