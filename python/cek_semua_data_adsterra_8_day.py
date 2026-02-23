#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra 8-Day Tracker (v3.7)
Author: Wahyu Kurniawan
Date: 2026-02-13
Description: 
    Script khusus untuk memantau performa 8 Hari Terakhir (Termasuk Hari Ini).
    
    [LOGIKA WAKTU]
    - Hari Ini (Day 1)
    - Mundur 7 hari ke belakang
    - Total Data: 8 Hari

Dependencies:
    - requests, tabulate, colorama
--------------------------------------------------------------------------------
"""

import sys
import json
import requests
from datetime import datetime, timedelta
import time

# Cek Library
try:
    from tabulate import tabulate
    from colorama import init, Fore, Style, Back
    init(autoreset=True) 
except ImportError:
    print("Error: Library belum lengkap.")
    print("Run: pip install tabulate colorama requests")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI (8 DAYS MODE)
# ==============================================================================

class Config:
    API_KEY = "d99b6eb88c389817b16af23dd030f280"
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    USER_AGENT = "WahyuBot/3.7 (8DaysMode)"
    
    # MUNDUR 7 HARI DARI HARI INI
    # (Hari Ini + 7 Hari Kebelakang = Total 8 Hari)
    DAYS_LOOKBACK = 7  

# ==============================================================================
# 2. CLIENT API
# ==============================================================================

class AdsterraClient:
    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/json"
        })

    def get_8days_stats(self):
        today = datetime.now()
        
        # Hitung Tanggal
        finish_date = today.strftime('%Y-%m-%d')
        # start_date = hari ini dikurangi 7 hari
        start_date = (today - timedelta(days=Config.DAYS_LOOKBACK)).strftime('%Y-%m-%d')

        params = {
            "start_date": start_date,
            "finish_date": finish_date,
            "group_by": "date" 
        }

        print(f"{Fore.CYAN}[SYSTEM] Mengambil Data 8 Hari Terakhir...")
        print(f"{Fore.CYAN}[SYSTEM] Periode: {Fore.YELLOW}{start_date}{Fore.CYAN} s/d {Fore.YELLOW}{finish_date}")
        
        try:
            start_time = time.time()
            resp = self.session.get(Config.BASE_URL, params=params, timeout=30)
            duration = time.time() - start_time
            
            print(f"{Fore.GREEN}[SUCCESS] Data diterima dalam {duration:.2f} detik.")

            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"{Fore.RED}[ERROR] HTTP Code: {resp.status_code}")
                return None
        except Exception as e:
            print(f"{Fore.RED}[CONN] Error: {e}")
            return None

# ==============================================================================
# 3. TAMPILAN LAPORAN
# ==============================================================================

def format_usd(val):
    return f"${float(val):,.3f}"

def format_num(val):
    return f"{int(val):,}".replace(",", ".")

def show_report(data):
    if not data or "items" not in data:
        print(f"{Fore.RED}Data kosong.")
        return

    items = data["items"]
    # Urutkan tanggal (Ascending)
    items = sorted(items, key=lambda x: x.get('date', '0000-00-00'))
    
    table_data = []
    total_rev = 0.0
    total_imp = 0
    
    print(f"\n{Fore.WHITE}Rincian Harian (8 Hari):\n")

    for item in items:
        date = item.get("date", "-")
        imp = item.get("impression", 0)
        cpm = item.get("cpm", 0.0)
        rev = item.get("revenue", 0.0)

        total_rev += rev
        total_imp += imp

        # --- LOGIKA PEWARNAAN ---
        
        # Revenue Hijau jika > 0
        rev_str = format_usd(rev)
        if rev > 12.0: # Highlight jika di atas $12 (High)
            rev_str = f"{Fore.GREEN}{Style.BRIGHT}{rev_str}{Style.RESET_ALL}"
        elif rev > 0:
            rev_str = f"{Fore.GREEN}{rev_str}{Style.RESET_ALL}"
        else:
            rev_str = f"{Fore.LIGHTBLACK_EX}{rev_str}{Style.RESET_ALL}"
        
        # CPM Kuning jika > $0.6
        cpm_str = format_usd(cpm)
        if cpm > 0.6:
            cpm_str = f"{Fore.YELLOW}{cpm_str}{Style.RESET_ALL}"

        table_data.append([
            date,
            format_num(imp),
            cpm_str,
            rev_str
        ])

    # Tampilkan Tabel
    headers = ["TANGGAL", "IMPRESSIONS", "CPM", "REVENUE"]
    print(tabulate(table_data, headers=headers, tablefmt="simple_grid", stralign="right"))

    # Summary Box
    print("\n" + "="*35)
    print(f"{Back.BLUE}{Fore.WHITE} TOTAL PENDAPATAN (8 HARI) {Style.RESET_ALL}")
    print("="*35)
    
    summary = [
        ["Total Impressions", format_num(total_imp)],
        ["Rata-rata Harian", format_usd(total_rev / len(items) if items else 0)],
        ["TOTAL REVENUE", f"{Fore.GREEN}{Style.BRIGHT}{format_usd(total_rev)}{Style.RESET_ALL}"]
    ]
    
    print(tabulate(summary, tablefmt="plain"))
    print("="*35 + "\n")

# ==============================================================================
# 4. START
# ==============================================================================

if __name__ == "__main__":
    # Header ASCII "8 DAYS"
    print(f"\n{Fore.CYAN}{Style.BRIGHT}")
    print(r"   ___    ____    ____  __   __ ____  ")
    print(r"  ( _ )  |  _ \  / /\ \ \ \ / // ___| ")
    print(r"  / _ \  | | | |/ /  \ \ \ V / \___ \ ")
    print(r" | (_) | | |_| / /   / /  | |   ___) |")
    print(r"  \___/  |____/_/   /_/   |_|  |____/ ")
    print(f"{Style.RESET_ALL}")
    
    print(f"User: Wahyu Kurniawan | Target: 8 Days (Inc. Today)")
    print("-" * 50)
    
    client = AdsterraClient(Config.API_KEY)
    res = client.get_8days_stats()
    
    if res:
        show_report(res)
        