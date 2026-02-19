#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra Revenue Tracker (v3.4 - Last 30 Days)
Author: Wahyu Kurniawan
Date: 2026-02-13
Description: 
    Script khusus untuk menarik Laporan Pendapatan Adsterra.
    
    [CHANGELOG v3.4]
    - UBAH: Rentang waktu otomatis menjadi 30 Hari Terakhir.
    - LAYOUT: Tetap menggunakan format bersih (Tanpa Clicks/CTR).
    - FITUR: Menambahkan indikator tren sederhana (Perbandingan rata-rata).

Dependencies:
    - requests
    - tabulate
    - colorama
--------------------------------------------------------------------------------
"""

import sys
import json
import requests
from datetime import datetime, timedelta
import time

# Bagian Import Library dengan Error Handling
try:
    from tabulate import tabulate
    from colorama import init, Fore, Style, Back
    # Inisialisasi colorama
    init(autoreset=True) 
except ImportError as e:
    print("Error: Library pendukung tidak ditemukan.")
    print(f"Detail: {e}")
    print("Solusi: Jalankan perintah 'pip install tabulate colorama requests'")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI GLOBAL
# ==============================================================================

class Config:
    # Kredensial API
    API_KEY = "d99b6eb88c389817b16af23dd030f280"
    
    # Endpoint API v3
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    
    # User Agent
    USER_AGENT = "WahyuKurniawan_Bot/3.4 (30DaysMode)"
    
    # Pengaturan Rentang Waktu
    DAYS_LOOKBACK = 30  # Mengambil data 30 hari ke belakang

# ==============================================================================
# 2. CLASS CLIENT API
# ==============================================================================

class AdsterraClient:
    """
    Menangani koneksi ke server Adsterra.
    """
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        
        # Header Autentikasi (Wajib X-API-Key)
        self.session.headers.update({
            "X-API-Key": self.api_key,
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/json"
        })

    def get_stats(self):
        """
        Mengambil statistik untuk 30 hari terakhir.
        """
        
        # 1. Menentukan Tanggal Dinamis
        today = datetime.now()
        
        # Tanggal Akhir = Hari Ini
        finish_date = today.strftime('%Y-%m-%d')
        
        # Tanggal Awal = Hari Ini dikurangi 30 Hari
        start_date_obj = today - timedelta(days=Config.DAYS_LOOKBACK)
        start_date = start_date_obj.strftime('%Y-%m-%d')

        # 2. Parameter Request
        params = {
            "start_date": start_date,
            "finish_date": finish_date,
            "group_by": "date" 
        }

        # 3. Log Visualisasi
        print(f"{Fore.CYAN}[SYSTEM] Mode: Laporan Bulanan (30 Hari)")
        print(f"{Fore.CYAN}[SYSTEM] Periode: {Fore.YELLOW}{start_date}{Fore.CYAN} s/d {Fore.YELLOW}{finish_date}")
        
        start_time = time.time()

        try:
            # Mengirim Request
            response = self.session.get(Config.BASE_URL, params=params, timeout=30)
            duration = time.time() - start_time
            
            print(f"{Fore.GREEN}[SUCCESS] Data diterima dalam {duration:.2f} detik.")

            if response.status_code == 200:
                data = response.json()
                if "errors" in data and data["errors"]:
                    print(f"{Fore.RED}[API ERROR] {data['errors']}")
                    return None
                return data
            
            # Error Handling HTTP
            elif response.status_code == 422:
                print(f"{Fore.YELLOW}[WARN] Validasi Gagal (422).")
            elif response.status_code == 401:
                print(f"{Fore.RED}[AUTH] Token API Salah/Expired.")
            else:
                print(f"{Fore.RED}[HTTP] Error Code: {response.status_code}")
                
            return None

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}[NETWORK] Koneksi Gagal: {str(e)}")
            return None

# ==============================================================================
# 3. MANAJEMEN TAMPILAN
# ==============================================================================

def format_currency(value):
    return f"${float(value):,.3f}"

def format_number(value):
    return f"{int(value):,}".replace(",", ".")

def display_clean_report(data):
    """
    Menampilkan data 30 hari terakhir.
    """
    
    if not data or "items" not in data:
        print(f"{Fore.RED}[ERROR] Data kosong.")
        return

    items = data["items"]
    total_days = len(items)
    
    if total_days == 0:
        print(f"{Fore.YELLOW}[INFO] Tidak ada data dalam 30 hari terakhir.")
        return

    table_rows = []
    
    # Variabel Total
    total_imp = 0
    total_rev = 0.0
    
    # Sorting Tanggal
    sorted_items = sorted(items, key=lambda x: x.get('date', '0000-00-00'))

    print(f"\n{Fore.WHITE}Menampilkan statistik harian...\n")

    for item in sorted_items:
        date = item.get("date", "-")
        imp = item.get("impression", 0)
        cpm = item.get("cpm", 0.0)
        rev = item.get("revenue", 0.0)

        total_imp += imp
        total_rev += rev

        # Logika Warna Baris
        rev_str = format_currency(rev)
        if rev > 0:
            rev_str = f"{Fore.GREEN}{rev_str}{Style.RESET_ALL}"
        else:
            rev_str = f"{Fore.LIGHTBLACK_EX}{rev_str}{Style.RESET_ALL}"
            
        cpm_str = format_currency(cpm)
        if cpm > 0.5: # Highlight jika CPM > $0.5
            cpm_str = f"{Fore.YELLOW}{cpm_str}{Style.RESET_ALL}"

        table_rows.append([
            date,
            format_number(imp),
            cpm_str,
            rev_str
        ])

    # Render Tabel
    headers = ["TANGGAL", "IMPRESSIONS", "CPM", "REVENUE"]
    print(tabulate(table_rows, headers=headers, tablefmt="simple_grid", stralign="right"))

    # Render Summary
    print("\n" + "="*40)
    print(f"{Back.BLUE}{Fore.WHITE}  30 DAYS REVENUE SUMMARY  {Style.RESET_ALL}")
    print("="*40)
    
    avg_daily_rev = total_rev / total_days if total_days > 0 else 0
    
    summary_data = [
        ["Periode", "30 Hari Terakhir"],
        ["Total Impressions", format_number(total_imp)],
        ["Rata-rata Revenue/Hari", format_currency(avg_daily_rev)],
        ["-----------------------", "----------------"],
        ["TOTAL PENDAPATAN", f"{Fore.GREEN}{Style.BRIGHT}{format_currency(total_rev)}{Style.RESET_ALL}"]
    ]
    
    print(tabulate(summary_data, tablefmt="plain"))
    print("="*40 + "\n")

# ==============================================================================
# 4. EKSEKUSI
# ==============================================================================

if __name__ == "__main__":
    # Header ASCII 30 Days
    print(f"\n{Fore.CYAN}{Style.BRIGHT}")
    print(r"  ____   ___   ____    _ __   __ ____  ")
    print(r" |___ \ / _ \ |  _ \  / \\ \ / // ___| ")
    print(r"   __) | | | || | | |/ _ \\ V / \___ \ ")
    print(r"  / __/| |_| || |_| / ___ \| |   ___) |")
    print(r" |_____|\___/ |____/_/   \_\_|  |____/ ")
    print(f"{Style.RESET_ALL}")
    
    print(f"User: Wahyu Kurniawan | Mode: Last 30 Days Only")
    print("-" * 50)

    client = AdsterraClient(Config.API_KEY)
    json_result = client.get_stats()
    
    if json_result:
        display_clean_report(json_result)
        