# Backup & restore: project BogaX, Cursor, dan dev stack

Panduan ini untuk skenario **format laptop**, **ganti mesin**, atau **upgrade OS** (mis. Ubuntu 22.04 → 24.04), agar Anda bisa memulihkan **kode**, **database**, **konfigurasi editor**, dan mengetahui apa yang harus **di-install ulang** di OS.

---

## 1. Prinsip singkat

| Sumber | Disimpan di mana | Ikut backup folder `bogax` saja? |
|--------|------------------|-----------------------------------|
| Kode + lockfile (`package-lock.json`, `requirements.txt`) | Folder project | Ya |
| `.env` (rahasia DB, secret Django) | Biasanya `backend/.env` | Ya, jika Anda sengaja backup (jangan commit ke Git publik) |
| Basis data PostgreSQL | Server Postgres, bukan folder project | **Tidak** — wajib `pg_dump` |
| Virtualenv Python (`.venv`) | Bisa di dalam project | Opsional; sering **lebih aman buat ulang** setelah OS baru |
| `node_modules` | `frontend/` | Opsional (besar); cukup `npm ci` / `npm install` |
| Setting Cursor | Home directory Linux | **Tidak** — backup terpisah (lihat §3) |
| Chat / state Cursor | `~/.cursor/` | **Tidak** — backup terpisah jika ingin riwayat chat |

---

## 2. Backup folder project (HDD eksternal / NAS)

### Yang sebaiknya ikut

- Seluruh repo **`bogax/`** (termasuk `.git` jika pakai Git lokal).
- File **`backend/.env`** (sandi DB, `DJANGO_SECRET_KEY`, dll.) — simpan di media terenkripsi atau arsip terpisah jika lebih aman.
- Opsional: **`frontend/node_modules`** dan **`.venv`** hanya jika Anda mau mengurangi waktu install; setelah OS baru sering lebih bersih tanpa keduanya.

### Yang bisa diabaikan (hemat ruang)

- `frontend/node_modules/`
- `.venv/` atau `backend/__pycache__/`, `**/*.pyc`
- `frontend/dist/`

### Contoh arsip dengan `tar` (dari induk folder workspace)

```bash
# Ganti path sesuai mesin Anda
cd "$HOME/Downloads/workspace"
tar --exclude='bogax/frontend/node_modules' \
    --exclude='bogax/.venv' \
    --exclude='bogax/frontend/dist' \
    -czvf /media/EXTERNAL/bogax-project-$(date +%Y%m%d).tar.gz bogax
```

Atau salin folder dengan **rsync** (bisa diulang; efisien):

```bash
rsync -a --delete \
  --exclude 'node_modules' \
  --exclude '.venv' \
  --exclude 'frontend/dist' \
  --exclude '__pycache__' \
  "$HOME/Downloads/workspace/bogax/" "/media/EXTERNAL/backup/bogax/"
```

---

## 3. Backup pengaturan Cursor (level OS / user)

Cursor di Linux mengikuti pola mirip VS Code. Lokasi umum (periksa di mesin Anda jika beda):

| Isi | Path tipikal |
|-----|----------------|
| Setting user, keybinding, snippet | `~/.config/Cursor/User/` |
| Daftar ekstensi (disarankan diekspor ke file) | lihat perintah di bawah |
| Data Cursor (chat, cache proyek, dll.) | `~/.cursor/` |

### 3a. Salin folder konfigurasi User (disarankan)

```bash
mkdir -p /media/EXTERNAL/backup/cursor-config
cp -a "$HOME/.config/Cursor/User/settings.json" /media/EXTERNAL/backup/cursor-config/ 2>/dev/null || true
cp -a "$HOME/.config/Cursor/User/keybindings.json" /media/EXTERNAL/backup/cursor-config/ 2>/dev/null || true
cp -a "$HOME/.config/Cursor/User/snippets" /media/EXTERNAL/backup/cursor-config/ 2>/dev/null || true
# Jika ada:
cp -a "$HOME/.config/Cursor/User/profiles" /media/EXTERNAL/backup/cursor-config/ 2>/dev/null || true
```

Atau arsip seluruh folder User:

```bash
tar -czvf /media/EXTERNAL/backup/cursor-user-$(date +%Y%m%d).tar.gz -C "$HOME/.config/Cursor" User
```

### 3b. Daftar ekstensi (untuk install ulang cepat)

Jika perintah `cursor` ada di PATH:

```bash
cursor --list-extensions > /media/EXTERNAL/backup/cursor-extensions.txt
```

Setelah restore OS, install ulang:

```bash
xargs -a /media/EXTERNAL/backup/cursor-extensions.txt -L1 cursor --install-extension
```

(Jika perintahnya `cursor` tidak tersedia di terminal, install ekstensi manual dari daftar file tersebut.)

### 3c. Riwayat chat & state Cursor (opsional)

```bash
tar -czvf /media/EXTERNAL/backup/cursor-dotcursor-$(date +%Y%m%d).tar.gz -C "$HOME" .cursor
```

Folder ini bisa besar; backup jika Anda ingin melanjutkan konteks chat lama.

### 3d. Rules AI di dalam project

Jika Anda memakai `.cursor/rules/` atau `AGENTS.md` **di dalam** folder `bogax`, itu **sudah ikut** backup project — tidak perlu langkah ekstra.

---

## 4. Backup database PostgreSQL (wajib untuk data)

Data tabel **tidak** ikut hanya dari salinan folder project.

### Dump satu database `bogax`

```bash
# Ganti user/host jika berbeda dengan backend/.env
pg_dump -h localhost -U goeska -d bogax -Fc -f /media/EXTERNAL/backup/bogax-$(date +%Y%m%d).dump
```

Format `-Fc` (custom) cocok untuk `pg_restore`.

### Restore di mesin baru (setelah Postgres terpasang dan user/DB dibuat)

```bash
createdb -h localhost -U goeska bogax   # jika DB belum ada
pg_restore -h localhost -U goeska -d bogax --clean --if-exists /path/ke/bogax-YYYYMMDD.dump
```

Sesuaikan nama user/password dengan `backend/.env` setelah restore.

---

## 5. Dev stack: apa yang “pulih otomatis” vs harus install ulang

Setelah **format / OS baru**, yang **tidak** pulih hanya dengan membuka folder:

- **OS**: Python, Node, PostgreSQL, Git, driver, dll.
- **Cursor**: aplikasi editor + ekstensi.
- **Layanan**: Postgres harus jalan, database di-restore dari dump.

Yang **pulih dari backup project** (setelah dependensi terpasang):

- Kode, konfigurasi Vite/Django, migrasi, dll.

### Checklist install di OS baru (sesuai README proyek)

1. **Git** (jika dipakai).
2. **Python 3.12+** — buat venv baru di project:
   ```bash
   cd /path/ke/bogax
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt
   ```
3. **Node.js 20+** dan npm:
   ```bash
   cd frontend && npm ci   # atau npm install
   ```
4. **PostgreSQL** — install service, buat role/database seperti di `.env`, lalu **restore** dump (§4).
5. Salin **`backend/.env`** dari backup jika belum ada.
6. **Cursor** — install dari situs Cursor, restore §3, buka folder `bogax`.

### Upgrade OS (tanpa format penuh)

- Biasanya **home** dan **konfig Cursor** tetap; tetap disarankan: backup §2–§4 sebelum upgrade besar.
- Setelah upgrade: cek `python3`, `node`, Postgres masih OK; jalankan lagi `pip install -r` / `npm ci` jika ada masalah library.

---

## 6. Urutan restore singkat (setelah laptop baru)

1. Install **PostgreSQL**, buat user DB + database `bogax` → **pg_restore**.
2. Taruh folder **`bogax`** kembali (mis. `~/Downloads/workspace/bogax`).
3. Restore **Cursor User** + **`.cursor`** (opsional) dari arsip §3.
4. Install **Cursor**, **ekstensi** dari `cursor-extensions.txt`.
5. Buat **`.venv`**, `pip install -r backend/requirements.txt`.
6. Di **frontend**: `npm ci` atau `npm install`.
7. Salin **`backend/.env`**.
8. `python manage.py migrate` (jika perlu) dan jalankan backend + frontend seperti di README.

---

## 7. Keamanan

- Jangan commit **`backend/.env`** ke repositori publik.
- Simpan dump DB dan arsip berisi secret di **disk terenkripsi** atau sandi arsip (`zip -e`, `gpg`, dll.) jika HDD bisa hilang.

Dokumen ini ikut di folder project; setelah backup `bogax`, panduan ini ikut ke HDD eksternal Anda.
