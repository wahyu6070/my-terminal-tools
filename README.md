# My Terminal Tools

Kumpulan *script* otomatisasi tingkat lanjut yang dirancang khusus untuk lingkungan **Termux (Android)** dan **Linux**. Repositori ini berisi sekumpulan alat untuk menyederhanakan alur kerja manajemen *website* statis (seperti Hugo) dan pelacakan pendapatan **Adsterra** secara otomatis melalui integrasi API.

##  Fitur Utama

Repositori ini dibagi menjadi dua fungsionalitas utama yang terintegrasi langsung ke dalam inti sistem:
1. *Git & Content Automation*: Alat cerdas untuk melakukan pembaruan *timestamp* pada file *Markdown* (`.md`) yang baru saja dimodifikasi dan melakukan proses *push* ke repositori secara mulus.
2. *Adsterra Revenue Trackers*: Rangkaian pelacak pendapatan Adsterra yang menarik data langsung dari server, memprosesnya, dan menampilkannya dalam format tabel CLI yang bersih, rapi, dan dilengkapi indikator warna performa.

##  Cara Instalasi Terpadu (One-Click Install)

Untuk menginstal seluruh *tools* ini ke dalam perangkat Anda, cukup salin dan jalankan perintah tunggal di bawah ini pada terminal Termux Anda.

*Script installer* ini akan secara otomatis:
- Melakukan pembaruan sistem dasar Termux.
- Menginstal dependensi inti (**Python**, **Hugo**, **Git**, **Golang**).
- Memasang pustaka Python yang dibutuhkan (`requests`, `tabulate`, `colorama`).
- Membangun lingkungan eksekusi Python yang **terisolasi** di dalam sistem.

```bash
pkg update -y && pkg install curl wget -y && curl -sL https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/start.sh -o start.sh && bash start.sh```
