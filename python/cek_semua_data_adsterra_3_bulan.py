#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra 90 Days + Monthly Meta (With Daily Average)
Author: Wahyu Kurniawan
Date: 2026-02-13
Description: 
    Menampilkan data harian 90 hari terakhir DAN ringkasan per bulan.
    
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
    API_KEY = "d99b6eb88c389817b16af23dd030f280"
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    USER_AGENT = "WahyuBot/4.1 (MonthlyAvgDaily)"
    
    # 90 Hari (3 Bulan)
    DAYS_LOOKBACK = 90  

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
        today = datetime.now()
        finish_date = today.strftime('%Y-%m-%d')
        start_date = (today - timedelta(days=Config.DAYS_LOOKBACK)).strftime('%Y-%m-%d')

        params = {
            "start_date": start_date,
            "finish_date": finish_date,
            "group_by": "date" 
        }

        print(f"{Fore.CYAN}[SYSTEM] Mengambil data 90 hari terakhir...")
        print(f"{Fore.CYAN}[SYSTEM] Periode: {Fore.YELLOW}{start_date}{Fore.CYAN} s/d {Fore.YELLOW}{finish_date}")
        
        try:
            start_time = time.time()
            resp = self.session.get(Config.BASE_URL, params=params, timeout=45)
            duration = time.time() - start_time
            
            print(f"{Fore.GREEN}[SUCCESS] Data diterima ({duration:.2f} detik).")
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as e:
            print(f"{Fore.RED}[CONN] Error: {e}")
            return None

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
    
    daily_rows = []
    
    # Dictionary Akumulasi: {'2026-02': {'imp': 0, 'rev': 0, 'days': 0}}
    monthly_agg = {} 
    
    print(f"\n{Fore.WHITE}Memproses statistik...\n")

    for item in items:
        # Data Mentah
        date = item.get("date", "-")
        imp = int(item.get("impression", 0))
        cpm = float(item.get("cpm", 0.0))
        rev = float(item.get("revenue", 0.0))

        # 1. TABEL HARIAN
        rev_str = format_usd(rev)
        if rev > 12.0: rev_str = f"{Fore.GREEN}{Style.BRIGHT}{rev_str}{Style.RESET_ALL}"
        elif rev > 0: rev_str = f"{Fore.GREEN}{rev_str}{Style.RESET_ALL}"
        else: rev_str = f"{Fore.LIGHTBLACK_EX}{rev_str}{Style.RESET_ALL}"
        
        cpm_str = format_usd(cpm)
        if cpm > 0.8: cpm_str = f"{Fore.YELLOW}{cpm_str}{Style.RESET_ALL}"

        daily_rows.append([date, format_num(imp), cpm_str, rev_str])

        # 2. LOGIKA META BULANAN
        month_key = date[:7] # Ambil YYYY-MM
        
        if month_key not in monthly_agg:
            monthly_agg[month_key] = {'imp': 0, 'rev': 0, 'days': 0}
            
        monthly_agg[month_key]['imp'] += imp
        monthly_agg[month_key]['rev'] += rev
        monthly_agg[month_key]['days'] += 1 # Tambah 1 hari setiap kali data ditemukan

    # --- RENDER TABEL HARIAN ---
    print(f"{Fore.CYAN}=== RINCIAN HARIAN (90 HARI TERAKHIR) ==={Style.RESET_ALL}")
    headers_daily = ["TANGGAL", "IMPRESSIONS", "CPM", "REVENUE"]
    print(tabulate(daily_rows, headers=headers_daily, tablefmt="simple_grid", stralign="right"))

    # --- RENDER TABEL META BULANAN (UPDATE FITUR BARU) ---
    print("\n" + "="*60)
    print(f"{Back.MAGENTA}{Fore.WHITE}  META DATA: PERFORMA BULANAN & RATA-RATA HARIAN  {Style.RESET_ALL}")
    print("="*60)
    
    monthly_rows = []
    sorted_months = sorted(monthly_agg.keys(), reverse=True)
    
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
    
    print("\n" + f"{Fore.WHITE}TOTAL AKUMULASI (90 HARI): {Fore.GREEN}{Style.BRIGHT}{format_usd(grand_total_rev)}{Style.RESET_ALL}")
    print("-" * 60 + "\n")

# ==============================================================================
# 4. MAIN
# ==============================================================================

if __name__ == "__main__":
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}ADSTERRA ANALYTICS PRO (v4.1){Style.RESET_ALL}")
    print("-" * 35)
    
    client = AdsterraClient(Config.API_KEY)
    res = client.get_stats()
    
    if res:
        show_report(res)
        