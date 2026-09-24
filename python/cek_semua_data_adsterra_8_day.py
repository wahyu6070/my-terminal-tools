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
    - requests, colorama
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
    from colorama import init
    init(autoreset=True)
    import adsterra_ui as ui
except ImportError:
    print("Error: Library belum lengkap.")
    print("Run: pip install colorama requests")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI (8 DAYS MODE)
# ==============================================================================

class Config:
    API_KEY = get_cached_api_key("62353c425ac1369b6a358b0e44b79377")
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


        try:
            start_time = time.time()
            resp = get_with_token_refresh(self.session, Config.BASE_URL, params=params, timeout=30)
            duration = time.time() - start_time

            if resp.status_code == 200:
                ui.fetch_ok(f"{start_date} s/d {finish_date}", duration)
                return resp.json()
            else:
                ui.error(f"[HTTP] Error {resp.status_code}")
                return None
        except Exception as e:
            ui.error(f"[CONN] Error: {e}")
            return None

# ==============================================================================
# 3. TAMPILAN LAPORAN
# ==============================================================================

def show_report(data):
    if not data or "items" not in data:
        ui.error("Data kosong.")
        return
    ui.print_daily_report(data["items"])

# ==============================================================================
# 4. START
# ==============================================================================

if __name__ == "__main__":
    ui.title("ADSTERRA · 8 HARI TERAKHIR", "Hari ini + 7 hari sebelumnya")

    client = AdsterraClient(Config.API_KEY)
    res = client.get_8days_stats()

    if res:
        show_report(res)
