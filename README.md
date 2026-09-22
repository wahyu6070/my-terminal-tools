# My Terminal Tools

Kumpulan *script* otomatisasi tingkat lanjut yang dirancang khusus untuk lingkungan **Termux (Android)** dan **Linux**. Repositori ini berisi sekumpulan alat untuk menyederhanakan alur kerja manajemen *website* statis (seperti Hugo) dan pelacakan pendapatan **Adsterra** secara otomatis melalui integrasi API.

##  Fitur Utama

Repositori ini dibagi menjadi dua fungsionalitas utama yang terintegrasi langsung ke dalam inti sistem:
1. *Git & Content Automation*: Alat cerdas untuk melakukan pembaruan *timestamp* pada file *Markdown* (`.md`) yang baru saja dimodifikasi dan melakukan proses *push* ke repositori secara mulus.
2. *Adsterra Revenue Trackers*: Rangkaian pelacak pendapatan Adsterra yang menarik data langsung dari server, memprosesnya, dan menampilkannya dalam format tabel CLI yang bersih, rapi, dan dilengkapi indikator warna performa.

Command `p` dan `push` memperbarui field `lastmod:` pada front matter Markdown yang baru dimodifikasi. Jika file lama hanya memiliki `date:`, field tersebut otomatis dikonversi menjadi `lastmod:`.

Command `c` menampilkan ringkasan seluruh bulan sejak Oktober 2022 sampai bulan berjalan. Command `d` menampilkan rincian harian untuk seluruh periode; keduanya otomatis membagi request agar mematuhi batas maksimal 366 hari dari API.

## Cara Instalasi Terpadu (One-Click Install)

Installer mendukung **Termux** dan **Ubuntu/Debian** serta menjalankan pelacak Adsterra dengan Python global sistem.

*Script installer* ini akan secara otomatis:
- Mengunduh script Python dan Git Automation.
- Memasang pustaka Python yang dibutuhkan (`requests`, `tabulate`, `colorama`) secara global.
- Membuat command `a`, `b`, `c`, `d`, `z`, `p`, dan `push`.

### Termux

```bash
pkg update -y && pkg install python curl git -y
curl -fsSL https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/start.sh | bash
```

### Ubuntu/Debian

Jalankan instalasi sebagai user biasa (bukan `sudo`):

```bash
sudo apt update && sudo apt install -y python3 python3-requests python3-tabulate python3-colorama curl git
curl -fsSL https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/start.sh | bash
```

Command Ubuntu dipasang di `~/.local/bin`. Bila belum tersedia di `PATH`:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## Pemulihan API Otomatis

Jika Adsterra menolak API key (HTTP 401/403 atau pesan autentikasi), script mengambil key terbaru dari `https://winlator.me/adstera.txt`, menyimpannya lokal dengan permission khusus pemilik, lalu mengulangi request satu kali. Koneksi atau format sumber yang gagal tidak akan menimpa key lama.
