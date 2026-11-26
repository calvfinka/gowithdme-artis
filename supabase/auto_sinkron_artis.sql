-- GoWithDME Artis: bangun ulang artis.gowithdme.com begitu event BERLINE-UP diterbitkan/diubah (tanpa menunggu jadwal harian).
-- Cara kerja: tabel events memicu kick_sinkron_artis(), yang memanggil GitHub API untuk menjalankan workflow "Sinkron artis"
-- di repo calvfinka/gowithdme-artis. Halaman terbit sekitar 2-4 menit kemudian. Jadwal harian di sinkron.yml tetap jalan sebagai cadangan.
-- Berdiri sendiri: fungsi, pemicu, dan tabel catatannya TIDAK memakai nama milik auto_sinkron.sql (repo utama) atau pemicu blog,
-- jadi ketiganya jalan berdampingan tanpa saling menahan. Aman dijalankan ulang.
--
-- LANGKAH SEKALI SAJA (sebelum menjalankan berkas ini):
--  1. Token GitHub yang sudah kamu pakai untuk repo utama dan blog (secret 'github_dispatch_token' di Vault) harus diberi akses ke repo baru:
--     GitHub > Settings > Developer settings > Fine-grained tokens > (token itu) > Repository access: tambahkan calvfinka/gowithdme-artis.
--     Permission tetap: Actions = Read and write.  Bila tokennya belum ada, buat dulu seperti di komentar auto_sinkron.sql.
--  2. Jalankan seluruh isi berkas ini di Supabase > SQL Editor.

create extension if not exists pg_net with schema extensions;

-- Catatan panggilan (RLS aktif tanpa policy = tidak terbaca lewat API publik). Tabel TERPISAH dari sinkron_log.
create table if not exists sinkron_log_artis(
  id bigserial primary key,
  at timestamptz not null default now(),
  tabel text,
  request_id bigint
);
alter table sinkron_log_artis enable row level security;

create or replace function kick_sinkron_artis() returns trigger
language plpgsql security definer set search_path = public, extensions, vault as $$
declare
  pub boolean; hasl boolean; tok text; rid bigint;
begin
  -- hanya bila ada event TERBIT berline-up yang berubah (draft, pengajuan, dan event tanpa line-up tidak memicu)
  if TG_OP = 'DELETE' then
    pub := (OLD.status = 'published'); hasl := coalesce(OLD.lineup, '') <> '';
  elsif TG_OP = 'INSERT' then
    pub := (NEW.status = 'published'); hasl := coalesce(NEW.lineup, '') <> '';
  else
    pub := (NEW.status = 'published' or OLD.status = 'published');
    hasl := (coalesce(NEW.lineup, '') <> '' or coalesce(OLD.lineup, '') <> '');
  end if;
  if not (pub and hasl) then return null; end if;

  -- satu panggilan per 5 detik (impor banyak baris sekaligus tidak membanjiri GitHub)
  if exists (select 1 from sinkron_log_artis where at > now() - interval '5 seconds') then return null; end if;

  select decrypted_secret into tok from vault.decrypted_secrets where name = 'github_dispatch_token' limit 1;
  if tok is null then return null; end if;

  select net.http_post(
    url     := 'https://api.github.com/repos/calvfinka/gowithdme-artis/actions/workflows/sinkron.yml/dispatches',
    body    := '{"ref":"main"}'::jsonb,
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || tok,
      'Accept', 'application/vnd.github+json',
      'X-GitHub-Api-Version', '2022-11-28',
      'User-Agent', 'gwm-supabase',
      'Content-Type', 'application/json')
  ) into rid;
  insert into sinkron_log_artis(tabel, request_id) values (TG_TABLE_NAME, rid);
  delete from sinkron_log_artis where at < now() - interval '14 days';
  return null;
exception when others then
  return null;   -- gagal memicu sinkron tidak boleh menggagalkan penyimpanan event
end $$;

revoke all on function kick_sinkron_artis() from public, anon, authenticated;

drop trigger if exists kick_sinkron_artis_events on events;
create trigger kick_sinkron_artis_events after insert or update or delete on events
  for each row execute function kick_sinkron_artis();

-- Uji: ubah satu event terbit yang punya line-up (mis. Simpan di Panel Admin), lalu cek GitHub > Actions: "Sinkron artis" mulai dalam hitungan detik.
-- Riwayat panggilan:   select * from sinkron_log_artis order by id desc limit 5;
-- Jawaban GitHub (204 = sukses):   select id, status_code, left(content,120) from net._http_response order by id desc limit 5;
