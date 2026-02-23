#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra Revenue Tracker (v3.3 - All Time & Clean Layout)
Author: Wahyu Kurniawan
Date: 2026-02-13
Description: 
    Script khusus untuk menarik Laporan Pendapatan Adsterra secara lengkap (All-Time).
    
    [CHANGELOG v3.3]
    - FITUR: Menarik data Sejak Awal (01-10-2022) secara default.
    - LAYOUT: Menghapus kolom 'Clicks' dan 'CTR' sesuai request.
    - LAYOUT: Fokus tampilan pada Impressions, CPM, dan Revenue.
    - CORE: Optimasi fetch data untuk rentang waktu panjang (tahunan).

Dependencies:
    - requests (Komunikasi HTTP)
    - tabulate (Format Tabel Rapi)
    - colorama (Pewarnaan Terminal)
--------------------------------------------------------------------------------
"""

import sys
import json
import requests
from datetime import datetime, timedelta
import time

# Bagian Import Library dengan Error Handling yang Informatif
try:
    from tabulate import tabulate
    from colorama import init, Fore, Style, Back
    # Inisialisasi colorama (autoreset=True agar warna tidak bocor ke baris lain)
    init(autoreset=True) 
except ImportError as e:
    print("Error: Library pendukung tidak ditemukan.")
    print(f"Detail: {e}")
    print("Solusi: Jalankan perintah 'pip install tabulate colorama requests'")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI GLOBAL (USER SETTINGS)
# ==============================================================================

class Config:
    # Kredensial API
    API_KEY = "d99b6eb88c389817b16af23dd030f280"
    
    # Endpoint API v3 (Menggunakan domain tools untuk stabilitas)
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    
    # User Agent agar request terdeteksi sebagai browser/client valid
    USER_AGENT = "WahyuKurniawan_Bot/3.3 (Android/Termux)"
    
    # TANGGAL MULAI (Sejak Awal Karir/Akun)
    # Format: YYYY-MM-DD
    START_DATE_ALL_TIME = "2022-10-01" 

# ==============================================================================
# 2. CLASS CLIENT API (LOGIKA UTAMA)
# ==============================================================================

class AdsterraClient:
    """
    Menangani koneksi ke server Adsterra, autentikasi header, 
    dan pengambilan data JSON.
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        
        # Konfigurasi Header HTTP
        # Token dikirim via header 'X-API-Key' (Wajib untuk API v3)
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/json"
        })

    def get_stats(self):
        """
        Mengambil statistik dari tanggal awal (2022) sampai hari ini.
        """
        
        # 1. Menentukan Rentang Waktu
        # Tanggal Akhir = Hari Ini
        finish_date = datetime.now().strftime('%Y-%m-%d')
        
        # Tanggal Awal = Konfigurasi Static (2022-10-01)
        start_date = Config.START_DATE_ALL_TIME

        # 2. Menyusun Parameter Request
        # Note: 'group_by=date' penting agar data terpecah per hari
        params = {
            "start_date": start_date,
            "finish_date": finish_date,
            "group_by": "date" 
        }

        # 3. Visualisasi Proses (Loading Indicator sederhana)
        print(f"{Fore.CYAN}[SYSTEM] Menginisialisasi koneksi ke Adsterra...")
        print(f"{Fore.CYAN}[SYSTEM] Rentang Data: {Fore.YELLOW}{start_date}{Fore.CYAN} s/d {Fore.YELLOW}{finish_date}")
        print(f"{Fore.LIGHTBLACK_EX}[DEBUG] Endpoint: {Config.BASE_URL}")
        
        start_time = time.time() # Timer untuk mengukur kecepatan request

        try:
            # Mengirim GET Request
            response = self.session.get(Config.BASE_URL, params=params, timeout=60)
            
            # Menghitung durasi
            duration = time.time() - start_time
            print(f"{Fore.GREEN}[SUCCESS] Respon diterima dalam {duration:.2f} detik.")

            # Parsing JSON
            if response.status_code == 200:
                data = response.json()
                
                # Cek logical error dari API
                if "errors" in data and data["errors"]:
                    print(f"{Fore.RED}[API ERROR] {data['errors']}")
                    return None
                    
                return data
            
            # Error Handling HTTP Code
            elif response.status_code == 422:
                print(f"{Fore.YELLOW}[WARN] Validasi Gagal (422). Cek parameter tanggal.")
            elif response.status_code == 401:
                print(f"{Fore.RED}[AUTH] Token API Salah/Expired.")
            elif response.status_code == 429:
                print(f"{Fore.RED}[LIMIT] Terlalu banyak request. Tunggu sebentar.")
            else:
                print(f"{Fore.RED}[HTTP] Error Code: {response.status_code}")
                
            return None

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}[NETWORK] Gagal terhubung ke internet/server.")
            print(f"{Fore.LIGHTBLACK_EX}Detail: {str(e)}")
            return None

# ==============================================================================
# 3. MANAJEMEN TAMPILAN (FORMATTING & OUTPUT)
# ==============================================================================

def format_currency(value):
    """Format Uang: $1,234.567"""
    return f"${float(value):,.3f}"

def format_number(value):
    """Format Angka: 1.000.000"""
    return f"{int(value):,}".replace(",", ".")

def display_clean_report(data):
    """
    Menampilkan data tanpa kolom Clicks dan CTR.
    Fokus: Date | Impression | CPM | Revenue
    """
    
    if not data or "items" not in data:
        print(f"{Fore.RED}[ERROR] Data kosong atau format JSON berubah.")
        return

    items = data["items"]
    total_days = len(items)
    
    if total_days == 0:
        print(f"{Fore.YELLOW}[INFO] Tidak ada data pendapatan ditemukan pada rentang ini.")
        return

    # List penampung baris tabel
    table_rows = []
    
    # Variabel Akumulasi (Total)
    total_imp = 0
    total_rev = 0.0
    # Kita tidak perlu hitung Clicks/CTR lagi
    
    # Sorting: Urutkan dari tanggal terlama ke terbaru
    sorted_items = sorted(items, key=lambda x: x.get('date', '0000-00-00'))

    print(f"\n{Fore.WHITE}Memproses {total_days} hari data transaksi...\n")

    for item in sorted_items:
        # Ekstraksi Data Aman
        date = item.get("date", "-")
        imp = item.get("impression", 0)
        cpm = item.get("cpm", 0.0)
        rev = item.get("revenue", 0.0)

        # Update Total
        total_imp += imp
        total_rev += rev

        # Logika Pewarnaan Baris (Highlight Profit)
        # Jika Revenue hari itu > $0, warnai revenue hijau
        rev_str = format_currency(rev)
        if rev > 0:
            rev_str = f"{Fore.GREEN}{rev_str}{Style.RESET_ALL}"
        else:
            rev_str = f"{Fore.LIGHTBLACK_EX}{rev_str}{Style.RESET_ALL}"
            
        # Jika CPM tinggi (> $0.5), tandai kuning
        cpm_str = format_currency(cpm)
        if cpm > 0.5:
            cpm_str = f"{Fore.YELLOW}{cpm_str}{Style.RESET_ALL}"

        # Menyusun Baris Tabel (Tanpa Clicks & CTR)
        table_rows.append([
            date,
            format_number(imp),
            cpm_str,
            rev_str
        ])

    # --- RENDER TABEL DATA ---
    headers = ["TANGGAL", "IMPRESSIONS", "CPM", "REVENUE"]
    
    # Menggunakan format 'simple_grid' agar rapi di layar HP (Termux)
    print(tabulate(table_rows, headers=headers, tablefmt="simple_grid", stralign="right"))

    # --- RENDER KOTAK TOTAL (SUMMARY) ---
    print("\n" + "="*40)
    print(f"{Back.BLUE}{Fore.WHITE}  LIFETIME REVENUE SUMMARY  {Style.RESET_ALL}")
    print("="*40)
    
    # Menghitung Rata-rata Harian
    avg_daily_rev = total_rev / total_days if total_days > 0 else 0
    
    summary_data = [
        ["Periode Data", f"{Config.START_DATE_ALL_TIME} s/d Hari Ini"],
        ["Total Hari Aktif", f"{total_days} Hari"],
        ["Total Impressions", format_number(total_imp)],
        ["Rata-rata Revenue/Hari", format_currency(avg_daily_rev)],
        ["-----------------------", "----------------"], # Separator
        ["TOTAL PENDAPATAN (ALL)", f"{Fore.GREEN}{Style.BRIGHT}{format_currency(total_rev)}{Style.RESET_ALL}"]
    ]
    
    print(tabulate(summary_data, tablefmt="plain"))
    print("="*40 + "\n")

# ==============================================================================
# 4. EKSEKUSI PROGRAM
# ==============================================================================

if __name__ == "__main__":
    # Header Logo ASCII (Raw String)
    print(f"\n{Fore.BLUE}{Style.BRIGHT}")
    print(r"   _  _  _  _  _  _  _   ")
    print(r"  / \/ \/ \/ \/ \/ \/ \  ")
    print(r" ( A | L | L | T | I | M | E ) ")
    print(r"  \_/\_/\_/\_/\_/\_/\_/  ")
    print(f"{Style.RESET_ALL}")
    
    print(f"User: Wahyu Kurniawan | Mode: Clean & Full History")
    print("-" * 50)

    # Inisialisasi & Eksekusi
    client = AdsterraClient(Config.API_KEY)
    
    # Ambil data
    json_result = client.get_stats()
    
    # Tampilkan
    if json_result:
        display_clean_report(json_result)
        