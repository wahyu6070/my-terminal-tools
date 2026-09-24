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
    - colorama
--------------------------------------------------------------------------------
"""

import sys
import json
import requests
from datetime import datetime, timedelta
import time
from adsterra_api import get_cached_api_key, get_with_token_refresh

# Bagian Import Library dengan Error Handling
try:
    from colorama import init
    # Inisialisasi colorama
    init(autoreset=True)
    import adsterra_ui as ui
except ImportError as e:
    print("Error: Library pendukung tidak ditemukan.")
    print(f"Detail: {e}")
    print("Solusi: Jalankan perintah 'pip install colorama requests'")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI GLOBAL
# ==============================================================================

class Config:
    # Kredensial API
    API_KEY = get_cached_api_key("62353c425ac1369b6a358b0e44b79377")

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

        start_time = time.time()

        try:
            # Mengirim Request
            response = get_with_token_refresh(self.session, Config.BASE_URL, params=params, timeout=30)
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "errors" in data and data["errors"]:
                    ui.error(f"[API ERROR] {data['errors']}")
                    return None
                ui.fetch_ok(f"{start_date} s/d {finish_date}", duration)
                return data

            # Error Handling HTTP
            elif response.status_code == 422:
                ui.error("[WARN] Validasi Gagal (422).")
            elif response.status_code in (401, 403):
                ui.error("[AUTH] API key masih ditolak setelah pembaruan otomatis.")
            else:
                ui.error(f"[HTTP] Error Code: {response.status_code}")

            return None

        except requests.exceptions.RequestException as e:
            ui.error(f"[NETWORK] Koneksi Gagal: {str(e)}")
            return None

# ==============================================================================
# 3. MANAJEMEN TAMPILAN
# ==============================================================================

def display_clean_report(data):
    """
    Menampilkan data 30 hari terakhir.
    """
    if not data or "items" not in data:
        ui.error("[ERROR] Data kosong.")
        return
    ui.print_daily_report(data["items"])

# ==============================================================================
# 4. EKSEKUSI
# ==============================================================================

if __name__ == "__main__":
    ui.title("ADSTERRA · 30 HARI TERAKHIR", "Hari ini + 30 hari sebelumnya")

    client = AdsterraClient(Config.API_KEY)
    json_result = client.get_stats()

    if json_result:
        display_clean_report(json_result)
