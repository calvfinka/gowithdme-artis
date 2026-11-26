# Ambil event terbit yang punya line-up dari Supabase -> data/events.json (bahan build.py).
# Jalankan:  python3 tools/gen_events.py   lalu   python3 tools/build.py
# Hanya membaca lewat kunci anon (publik, dijaga RLS): event berstatus published. Kolomnya sengaja dipersempit
# ke yang dipakai halaman artis supaya egress Supabase kecil. Kunci boleh ditimpa lewat SUPABASE_URL / SUPABASE_ANON_KEY.
import os,sys,json,urllib.request,urllib.parse
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
URL=os.environ.get("SUPABASE_URL","https://jhqkylnqvhrljpaknjcg.supabase.co").rstrip("/")
KEY=os.environ.get("SUPABASE_ANON_KEY","sb_publishable_WEpourxfk4IKga2XyxKucQ_hkmxuJnY")
COLS="slug,title,title_en,category,venue,event_date,end_date,lineup,price_label,poster_url,ticket_url,created_at,cities(name)"
q=urllib.parse.urlencode({"select":COLS,"status":"eq.published","lineup":"not.is.null","order":"event_date.asc","limit":"2000"},safe="*,().")
req=urllib.request.Request(f"{URL}/rest/v1/events?{q}",headers={"apikey":KEY,"Authorization":"Bearer "+KEY})
try: rows=json.load(urllib.request.urlopen(req,timeout=60))
except Exception as e: sys.exit(f"gagal mengambil event: {e}")
if not rows: sys.exit("Supabase mengembalikan 0 event: data lama dibiarkan (cek RLS atau kunci).")
out=[]
for r in rows:
    r["city"]=(r.pop("cities",None) or {}).get("name")
    out.append(r)
os.makedirs(ROOT+"/data",exist_ok=True)
json.dump(out,open(ROOT+"/data/events.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print(len(out),"event ->","data/events.json")
