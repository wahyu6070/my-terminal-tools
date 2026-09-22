#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra All-Months Summary
Author: Wahyu Kurniawan
Date: 2026-02-13
Description:
    Menampilkan ringkasan setiap bulan sejak awal data.

    [FITUR BARU v4.1]
    - Rata-rata Harian Per Bulan: Menghitung (Total Revenue / Jumlah Hari).
      Contoh: Jika Februari dapat $150 dalam 10 hari, rata-ratanya $15/hari.

    [FITUR STANDAR]
    - Meta Bulanan: Total Impress, Avg CPM, Total Revenue.
    - Bahasa Indonesia untuk nama bulan.

Dependencies:
    - requests, tabulate, colorama
--------------------------------------------------------------------------------
"""

import sys
import json
import requests
from datetime import datetime, timedelta
import time
from adsterra_api import get_cached_api_key, get_with_token_refresh

# Cek Library
try:
    from tabulate import tabulate
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
except ImportError:
    print("Error: Library kurang.")
    print("Run: pip install tabulate colorama requests")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI
# ==============================================================================

class Config:
    API_KEY = get_cached_api_key("62353c425ac1369b6a358b0e44b79377")
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    USER_AGENT = "WahyuBot/4.1 (MonthlyAvgDaily)"

    START_DATE_ALL_TIME = "2022-10-01"

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

    def get_stats(self):
        first_date = datetime.strptime(Config.START_DATE_ALL_TIME, "%Y-%m-%d")
        final_date = datetime.now()
        chunk_start = first_date
        chunk_number = 0
        all_items = []

        print(f"{Fore.CYAN}[SYSTEM] Mengambil seluruh data bulanan...")
        print(f"{Fore.CYAN}[SYSTEM] Periode: {Fore.YELLOW}{first_date:%Y-%m-%d}{Fore.CYAN} s/d {Fore.YELLOW}{final_date:%Y-%m-%d}")

        while chunk_start.date() <= final_date.date():
            chunk_end = min(chunk_start + timedelta(days=365), final_date)
            chunk_number += 1
            params = {
                "start_date": chunk_start.strftime("%Y-%m-%d"),
                "finish_date": chunk_end.strftime("%Y-%m-%d"),
                "group_by": "date"
            }
            print(f"{Fore.CYAN}[FETCH {chunk_number}] {params['start_date']} s/d {params['finish_date']}")

            try:
                started = time.time()
                response = get_with_token_refresh(
                    self.session, Config.BASE_URL, params=params, timeout=60
                )
                duration = time.time() - started
            except requests.exceptions.RequestException as error:
                print(f"{Fore.RED}[CONN] Error: {error}")
                return None

            if response.status_code != 200:
                print(f"{Fore.RED}[HTTP] Error {response.status_code}: {response.text}")
                return None

            data = response.json()
            if data.get("errors"):
                print(f"{Fore.RED}[API ERROR] {data['errors']}")
                return None

            all_items.extend(data.get("items", []))
            print(f"{Fore.GREEN}[SUCCESS] Bagian {chunk_number} diterima ({duration:.2f} detik).")
            chunk_start = chunk_end + timedelta(days=1)

        return {"items": all_items, "itemCount": len(all_items)}

# ==============================================================================
# 3. LOGIKA TAMPILAN & META BULANAN
# ==============================================================================

def format_usd(val):
    return f"${float(val):,.3f}"

def format_num(val):
    return f"{int(val):,}".replace(",", ".")

def get_indo_month(date_str):
    """Mengubah '2026-02' menjadi 'Februari 2026'"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m')
        bulan_indo = {
            'January': 'Januari', 'February': 'Februari', 'March': 'Maret',
            'April': 'April', 'May': 'Mei', 'June': 'Juni',
            'July': 'Juli', 'August': 'Agustus', 'September': 'September',
            'October': 'Oktober', 'November': 'November', 'December': 'Desember'
        }
        month_en = dt.strftime('%B')
        year = dt.strftime('%Y')
        return f"{bulan_indo.get(month_en, month_en)} {year}"
    except:
        return date_str

def show_report(data):
    if not data or "items" not in data:
        print(f"{Fore.RED}Data kosong.")
        return

    items = data["items"]
    items = sorted(items, key=lambda x: x.get('date', '0000-00-00'))

    # Dictionary Akumulasi: {'2026-02': {'imp': 0, 'rev': 0, 'days': 0}}
    monthly_agg = {}

    print(f"\n{Fore.WHITE}Memproses statistik...\n")

    for item in items:
        # Data Mentah
        date = item.get("date", "-")
        imp = int(item.get("impression", 0))
        rev = float(item.get("revenue", 0.0))

        # LOGIKA META BULANAN
        month_key = date[:7] # Ambil YYYY-MM

        if month_key not in monthly_agg:
            monthly_agg[month_key] = {'imp': 0, 'rev': 0, 'days': 0}

        monthly_agg[month_key]['imp'] += imp
        monthly_agg[month_key]['rev'] += rev
        monthly_agg[month_key]['days'] += 1 # Tambah 1 hari setiap kali data ditemukan

    # --- RENDER TABEL META BULANAN ---
    print("\n" + "="*60)
    print(f"{Back.MAGENTA}{Fore.WHITE}  META DATA: PERFORMA BULANAN & RATA-RATA HARIAN  {Style.RESET_ALL}")
    print("="*60)

    monthly_rows = []
    # Urutkan kronologis: bulan paling lama di atas, paling baru di bawah.
    sorted_months = sorted(monthly_agg.keys())

    grand_total_rev = 0
    grand_total_imp = 0

    for m_key in sorted_months:
        data_bulan = monthly_agg[m_key]

        t_imp = data_bulan['imp']
        t_rev = data_bulan['rev']
        t_days = data_bulan['days'] # Jumlah hari aktif di bulan itu

        # Hitung Real CPM
        real_avg_cpm = (t_rev / t_imp * 1000) if t_imp > 0 else 0

        # Hitung Rata-rata Revenue Per Hari (Fitur Baru)
        avg_daily_rev = (t_rev / t_days) if t_days > 0 else 0

        # Formatting Tampilan
        nama_bulan = get_indo_month(m_key)

        rev_disp = f"{Fore.GREEN}{Style.BRIGHT}{format_usd(t_rev)}{Style.RESET_ALL}"
        cpm_disp = f"{Fore.YELLOW}{format_usd(real_avg_cpm)}{Style.RESET_ALL}"

        # Kolom Baru: Rata-rata Harian
        avg_daily_disp = format_usd(avg_daily_rev)

        monthly_rows.append([
            nama_bulan,
            t_days, # Jumlah Hari
            format_num(t_imp),
            cpm_disp,
            avg_daily_disp, # Kolom Baru
            rev_disp
        ])

        grand_total_rev += t_rev
        grand_total_imp += t_imp

    # Header Tabel Bulanan
    headers_monthly = ["BULAN", "HARI", "TOT IMPRESS", "AVG CPM", "RATA2 / HARI", "TOT REVENUE"]
    print(tabulate(monthly_rows, headers=headers_monthly, tablefmt="fancy_grid", stralign="right"))

    print("\n" + f"{Fore.WHITE}TOTAL AKUMULASI (SEMUA BULAN): {Fore.GREEN}{Style.BRIGHT}{format_usd(grand_total_rev)}{Style.RESET_ALL}")
    print("-" * 60 + "\n")

# ==============================================================================
# 4. MAIN
# ==============================================================================

if __name__ == "__main__":
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}ADSTERRA ALL-MONTHS ANALYTICS (v5.0){Style.RESET_ALL}")
    print("-" * 35)

    client = AdsterraClient(Config.API_KEY)
    res = client.get_stats()

    if res:
        show_report(res)
