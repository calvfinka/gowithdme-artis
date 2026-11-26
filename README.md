# GoWithDME Artis

Direktori artis dan pengisi acara konser/festival di **https://artis.gowithdme.com** (Indonesia `/id/`, Inggris `/en/`).
Dipisah dari repo utama [gowithdme](https://github.com/calvfinka/gowithdme). Situs statis di GitHub Pages; datanya dari Supabase (hanya baca, kunci anon).

## Isi repo
```
id/ en/              halaman publik (DIBUAT OTOMATIS oleh tools/build.py, jangan edit tangan)
index.html           pengalih bahasa di akar situs        404.html   sitemap.xml   robots.txt   (juga otomatis)
src/                 sumber tampilan: artist-page.* (halaman artis), artists-index.* (indeks)
tools/               gen_events.py (ambil data), build.py (bangun), cek_hasil.py (periksa), serve.py (uji lokal)
data/events.json     event berline-up dari Supabase (diperbarui workflow)
js/theme.js          tema terang/gelap       assets/favicon.svg
supabase/            auto_sinkron_artis.sql (pemicu bangun ulang otomatis)
.github/workflows/   sinkron.yml
```

## Cara kerja
Tiap nama di kolom `lineup` sebuah event menjadi satu halaman artis (`/id/<slug>`). Halaman event, poster, dan tombol tiket tetap di situs utama
(`https://gowithdme.com/<bahasa>/e/<slug>`), jadi semua tautan ke event berupa alamat penuh.

**Sinkron** (`.github/workflows/sinkron.yml`): sehari sekali (status "H-n" ikut segar), segera setelah event berline-up terbit (pemicu Supabase), saat `src/tools/js` diubah, atau manual di Actions > "Sinkron artis" > Run workflow. Workflow mengambil data, membangun, memeriksa hasil (`cek_hasil.py`), lalu commit bila berubah.

## Uji lokal
```
python3 tools/gen_events.py          # ambil data terbaru (butuh internet)
GWM_SITE=http://localhost:8000 python3 tools/build.py
python3 tools/cek_hasil.py
python3 tools/serve.py 8000          # buka http://localhost:8000/id/
npm test                             # uji logika status mendatang/berlangsung/selesai
```
Variabel build: `GWM_SITE` (alamat situs ini), `GWM_MAIN` (situs utama, default https://gowithdme.com), `GWM_TODAY` (paksa tanggal, format YYYY-MM-DD), `GWM_VER` (versi `?v=`).

## Aturan yang harus dijaga
- **Logika nama -> slug harus sama dengan repo utama.** `split_lineup`, `_akey`, `_aslug`, dan perulangan `ARTISTS` ada di `tools/build.py` di kedua repo. Halaman event di repo utama menaut ke `artis.gowithdme.com/<bahasa>/<slug>`; bila logikanya beda, tautan bisa mengarah ke halaman yang tidak ada. Ubah di satu repo, ubah juga di satunya.
- Jangan menaruh kunci rahasia di repo. Yang ada hanya kunci anon Supabase (publik, dijaga RLS), sama seperti di repo utama.
- Folder `id/` dan `en/` ditulis ulang tiap build.
