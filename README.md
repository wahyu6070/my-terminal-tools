
## 🛠️ Persiapan & Instalasi (Requirements)

Script ini membutuhkan beberapa library tambahan agar semua fitur (termasuk kompresi gambar dan *beautifier*) berjalan lancar.

### 1\. System Dependencies (Khusus Pengguna Termux)

Sebelum menginstall module Python, wajib install library sistem ini agar `Pillow` (Image Compressor) tidak error saat di-build:

```bash
pkg update && pkg upgrade
pkg install libjpeg-turbo libpng zlib
```

### 2\. Python Modules

Jalankan perintah berikut untuk menginstall seluruh dependency Python sekaligus:

```bash
pip install beautifulsoup4 mdformat mdformat-gfm mdformat-frontmatter requests Pillow
```

### 📋 Penjelasan Module

| Module | Kegunaan dalam Script Master Tools |
| :--- | :--- |
| **BeautifulSoup4** | Membaca struktur HTML untuk pengecekan *typo* syntax & *scraping* tabel ROM. |
| **Mdformat** | Merapikan format Markdown agar standar dan rapi. |
| **Mdformat Plugins** | (`-gfm`, `-frontmatter`) Menjaga agar *header* Hugo (Front Matter) tidak rusak saat dirapikan. |
| **Requests** | Mengirim request HTTP untuk mendeteksi Link Mati (*Dead Links*) di folder Public/Content. |
| **Pillow (PIL)** | Mengompres, mengubah ukuran (*resize*), dan konversi gambar ke format WebP (Menu 6). |

