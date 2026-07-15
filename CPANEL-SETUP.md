# Setup cPanel Hostinger untuk SEO Auto-Pilot

> Panduan menjalankan automation di hosting Hostinger via SSH + Cron Job.
> Gratis, no GitHub Actions billing.

---

## Prerequisites

- ✅ Akun Hostinger dengan akses **SSH** (cek di hPanel → Files → SSH Access)
- ✅ Akses **Cron Jobs** di cPanel
- ✅ Python 3.9+ (biasanya sudah ada di Hostinger)
- ✅ Repo GitHub `ReqTimeout/foryoutour` (sudah ada)

---

## Step 1: SSH ke Server Hostinger

```bash
ssh u123456789@your-domain.com
# atau pakai IP: ssh u123456789@123.45.67.89 -p 65002
```

(Username & port ada di hPanel → Files → SSH Access)

---

## Step 2: Clone Repo GitHub ke Server

```bash
cd ~
git clone https://github.com/ReqTimeout/foryoutour.git
cd foryoutour
```

---

## Step 3: Setup SSH Key untuk Push ke GitHub

```bash
# Generate key
ssh-keygen -t ed25519 -C "hostinger-seo" -f ~/.ssh/github_deploy_key
# Tekan enter 2x untuk passphrase kosong

# Tampilkan public key
cat ~/.ssh/github_deploy_key.pub
```

Copy output-nya, lalu:
1. Buka https://github.com/ReqTimeout/foryoutour/settings/keys
2. **Add deploy key** → Title: `Hostinger SEO` → Paste key → **Allow write access** ✅
3. Save

---

## Step 4: Konfigurasi SSH agar Pakai Key yang Tepat

```bash
cat >> ~/.ssh/config << 'EOF'
Host github.com
    IdentityFile ~/.ssh/github_deploy_key
    StrictHostKeyChecking no
EOF
```

---

## Step 5: Test Push dari Server

```bash
cd ~/foryoutour
git config user.name "foryoutour-hostinger"
git config user.email "seo@hostinger.foryoutours.com"

# Test pull + push
git pull
touch test.txt
git add test.txt
git commit -m "test ssh"
git push
rm test.txt
git add test.txt
git commit -m "cleanup"
git push
```

Kalau **push berhasil** → lanjut Step 6. Kalau **gagal** → cek SSH key sudah ditambahkan dengan write access.

---

## Step 6: Test Script Manual

```bash
cd ~/foryoutour
chmod +x scripts/deploy_hostinger.sh
bash scripts/deploy_hostinger.sh
tail -50 foryoutour-seo.log
```

Kalau log menunjukkan "20 articles refreshed" dan "Pushed to GitHub" → berhasil ✅

---

## Step 7: Setup Cron Job di cPanel

1. Login ke **cPanel** (bukan hPanel)
2. Cari menu **"Cron Jobs"** (di section Advanced)
3. **Common Settings**: pilih **"Every 4 hours"**
4. **Command**:
   ```bash
   bash /home/u123456789/foryoutour/scripts/deploy_hostinger.sh
   ```
   (Ganti `u123456789` dengan username cPanel kamu — cek di hPanel → Files → home directory)

5. Klik **"Add New Cron Job"**

---

## Step 8: Monitor

```bash
# Lihat log
tail -f ~/foryoutour-seo.log

# Lihat last 100 entries
tail -100 ~/foryoutour-seo.log | grep -E "Start|Complete|refreshed|Pushed"
```

---

## Troubleshooting

### "Permission denied" saat git push
→ SSH key belum ditambahkan ke GitHub atau belum `Allow write access`

### "Repository not found"
→ SSH key salah atau belum di-link ke `github.com` di `~/.ssh/config`

### "python3: command not found"
→ Cek `which python3` atau `which python`. Ganti `PYTHON=` di `deploy_hostinger.sh`

### "posts.json too big, skipping"
→ Normal kalau file sudah > 150 MB. Naikkan `MAX_POSTS_SIZE_MB` di script, atau hapus `articles` lama dari data

### Cron tidak jalan
1. Cek cPanel → Cron Jobs → pastikan entry ada
2. Cek email di cPanel → cron biasanya kirim email kalau error
3. Test manual: `bash /home/USERNAME/foryoutour/scripts/deploy_hostinger.sh`

---

## Jadwal Eksekusi

| Waktu (UTC) | Aksi |
|-------------|------|
| Setiap 4 jam | Freshness 20 artikel + commit + push |
| Minggu | Rotate links 300 artikel |
| Tanggal 1 & 15 | Keyword research + generate 100+ artikel baru |
| Jam 00:00 UTC | Ping sitemaps Google/Bing/Yandex |

**Worker Cloudflare tetap jalan** untuk IndexNow 2x/hari (06:00 & 18:00 UTC).

---

## Cek Status

```bash
# Cron job terakhir kali jalan
ls -la ~/foryoutour-seo.log
# Last modification = last run time

# Jumlah commit di bulan ini
cd ~/foryoutour && git log --since="30 days ago" --oneline | grep "auto:" | wc -l

# Total artikel
ls -la src/data/posts.json | awk '{print $5/1024/1024 " MB"}'
```

---

## Uninstall

```bash
# Hapus cron job di cPanel UI
# Hapus deploy key di GitHub
# Hapus folder repo
rm -rf ~/foryoutour
# Hapus SSH key
rm ~/.ssh/github_deploy_key*
```
