#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra Smart JSON Exporter (Clean Data + Rich Meta)
Location: src/adsterra_export_json.py
Author: Wahyu Kurniawan
Date: 2026-02-13
Description: 
    Mengekspor data statistik Adsterra dengan struktur JSON yang sangat spesifik:
    1. 'meta': Berisi rangkuman detail, statistik agregat, dan rekor performa.
    2. 'daily_stats': List harian yang BERSIH (hanya Impression, CPM, Revenue).

    [FITUR BARU]
    - Auto-detect 'Best Day' (Hari dengan pendapatan tertinggi).
    - Menghitung rata-rata harian secara otomatis di Meta.
    - Output harian ramping (hemat size file).

Dependencies:
    - requests, json
--------------------------------------------------------------------------------
"""

import sys
import json
import requests
import os
import time
from datetime import datetime

# Pewarnaan Terminal
class Col:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ==============================================================================
# 1. KONFIGURASI
# ==============================================================================

class Config:
    API_KEY = "d99b6eb88c389817b16af23dd030f280"
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    START_DATE = "2022-10-01" # Sejak Awal
    OUTPUT_DIR = "output_json"

# ==============================================================================
# 2. LOGIKA PEMROSESAN DATA
# ==============================================================================

def get_stats_from_api():
    """Mengambil raw data dari API"""
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n{Col.BOLD}=== EKSPOR DATA ADSTERRA (CLEAN MODE) ==={Col.RESET}")
    print(f"{Col.CYAN}[API] Mengambil data dari {Config.START_DATE} s/d {end_date}...{Col.RESET}")

    session = requests.Session()
    session.headers.update({
        "X-API-Key": Config.API_KEY,
        "User-Agent": "AdsterraCleanExporter/3.0"
    })

    params = {
        "start_date": Config.START_DATE,
        "finish_date": end_date,
        "group_by": "date"
    }

    try:
        resp = session.get(Config.BASE_URL, params=params, timeout=60)
        if resp.status_code == 200:
            data = resp.json()
            if "items" in data:
                return data["items"]
        
        print(f"{Col.RED}[ERROR] Gagal mengambil data. HTTP: {resp.status_code}{Col.RESET}")
        return None
    except Exception as e:
        print(f"{Col.RED}[CONN ERROR] {e}{Col.RESET}")
        return None

def process_smart_json(raw_items):
    """
    Mengolah data:
    - Meta: Detail & Lengkap
    - Items: Bersih & Minimalis
    """
    print(f"{Col.YELLOW}[PROCESS] Mengkalkulasi statistik & membersihkan data...{Col.RESET}")

    # 1. Persiapan Variabel Agregat
    clean_daily_data = []
    total_rev = 0.0
    total_imp = 0
    total_cpm_accum = 0.0
    
    # Variabel untuk mencari Hari Terbaik (Best Performance)
    best_day = {"date": None, "revenue": -1.0}

    # 2. Loop Data Harian (Cleaning)
    # Kita sort dulu berdasarkan tanggal
    sorted_items = sorted(raw_items, key=lambda x: x.get('date', '0000-00-00'))

    for item in sorted_items:
        # Ambil data penting saja
        date = item.get('date')
        imp = int(item.get('impression', 0))
        rev = float(item.get('revenue', 0.0))
        cpm = float(item.get('cpm', 0.0))

        # Update Agregat
        total_rev += rev
        total_imp += imp
        total_cpm_accum += cpm
        
        # Cek Rekor (Best Day)
        if rev > best_day["revenue"]:
            best_day = {"date": date, "revenue": rev, "cpm": cpm}

        # Masukkan ke list bersih (HANYA 4 FIELD INI)
        clean_daily_data.append({
            "date": date,
            "impression": imp,
            "cpm": cpm,
            "revenue": rev
        })

    # 3. Hitung Rata-rata
    days_count = len(clean_daily_data)
    avg_rev = total_rev / days_count if days_count > 0 else 0
    avg_cpm = total_cpm_accum / days_count if days_count > 0 else 0

    # 4. Susun Struktur JSON Akhir
    final_structure = {
        # --- META: SANGAT DETAIL ---
        "meta": {
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "period": {
                "start": Config.START_DATE,
                "end": datetime.now().strftime('%Y-%m-%d'),
                "total_days_active": days_count
            },
            "financial_summary": {
                "total_revenue_usd": round(total_rev, 3), # Total Uang
                "average_daily_revenue": round(avg_rev, 3), # Rata2 per hari
                "average_cpm": round(avg_cpm, 2)
            },
            "traffic_summary": {
                "total_impressions": total_imp,
                "average_daily_impressions": int(total_imp / days_count) if days_count else 0
            },
            "highlights": {
                "best_performing_day": best_day, # Hari paling cuan
                "currency": "USD"
            }
        },
        
        # --- DATA: SANGAT BERSIH ---
        "daily_stats": clean_daily_data
    }

    return final_structure

def save_file(data):
    if not os.path.exists(Config.OUTPUT_DIR):
        os.makedirs(Config.OUTPUT_DIR)
        
    filename = f"adsterra_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(Config.OUTPUT_DIR, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2) # Indent 2 agar hemat space tapi terbaca
            
        print("-" * 50)
        print(f"{Col.GREEN}✅ SUKSES! File JSON tersimpan.{Col.RESET}")
        print(f"📂 Path : {Col.BOLD}{filepath}{Col.RESET}")
        print(f"💰 Total Revenue: ${data['meta']['financial_summary']['total_revenue_usd']}")
        print(f"🏆 Best Day     : {data['meta']['highlights']['best_performing_day']['date']} (${data['meta']['highlights']['best_performing_day']['revenue']})")
        print("-" * 50)
    except Exception as e:
        print(f"{Col.RED}Gagal menyimpan file: {e}{Col.RESET}")

# ==============================================================================
# 3. MAIN
# ==============================================================================

if __name__ == "__main__":
    raw = get_stats_from_api()
    if raw:
        clean_json = process_smart_json(raw)
        save_file(clean_json)
        