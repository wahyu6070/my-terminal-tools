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
    from colorama import init, Fore, Style
    init(autoreset=True)
    import adsterra_ui as ui
except ImportError:
    print("Error: Library kurang.")
    print("Run: pip install colorama requests")
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


        while chunk_start.date() <= final_date.date():
            chunk_end = min(chunk_start + timedelta(days=365), final_date)
            chunk_number += 1
            params = {
                "start_date": chunk_start.strftime("%Y-%m-%d"),
                "finish_date": chunk_end.strftime("%Y-%m-%d"),
                "group_by": "date"
            }

            try:
                started = time.time()
                response = get_with_token_refresh(
                    self.session, Config.BASE_URL, params=params, timeout=60
                )
                duration = time.time() - started
            except requests.exceptions.RequestException as error:
                ui.error(f"[CONN] Error: {error}")
                return None

            if response.status_code != 200:
                ui.error(f"[HTTP] Error {response.status_code}: {response.text}")
                return None

            data = response.json()
            if data.get("errors"):
                ui.error(f"[API ERROR] {data['errors']}")
                return None

            all_items.extend(data.get("items", []))
            ui.fetch_ok(f"[{chunk_number}] {params['start_date']} s/d {params['finish_date']}", duration)
            chunk_start = chunk_end + timedelta(days=1)

        return {"items": all_items, "itemCount": len(all_items)}

# ==============================================================================
# 3. LOGIKA TAMPILAN & META BULANAN
# ==============================================================================

def aggregate_monthly(items):
    """Kelompokkan data harian menjadi {'YYYY-MM': {'imp', 'rev', 'days'}}."""
    monthly = {}
    for item in items:
        month_key = item.get("date", "-")[:7]
        agg = monthly.setdefault(month_key, {"imp": 0, "rev": 0.0, "days": 0})
        agg["imp"] += int(item.get("impression", 0))
        agg["rev"] += float(item.get("revenue", 0.0))
        agg["days"] += 1  # Hari yang memiliki data
    return monthly

def month_stats(agg):
    cpm = (agg["rev"] / agg["imp"] * 1000) if agg["imp"] > 0 else 0
    daily = (agg["rev"] / agg["days"]) if agg["days"] > 0 else 0
    return cpm, daily

def show_report(data):
    if not data or not data.get("items"):
        ui.error("Data kosong.")
        return

    monthly = aggregate_monthly(data["items"])
    months = sorted(monthly)  # Kronologis: bulan paling lama di atas
    current_month = datetime.now().strftime("%Y-%m")

    year_rev = {}
    for m_key in months:
        year_rev[m_key[:4]] = year_rev.get(m_key[:4], 0.0) + monthly[m_key]["rev"]

    total = {"imp": 0, "rev": 0.0, "days": 0}
    rows = []
    prev_daily = None
    current_year = None
    for m_key in months:
        agg = monthly[m_key]
        cpm, daily = month_stats(agg)
        for key in total:
            total[key] += agg[key]

        if m_key[:4] != current_year:
            current_year = m_key[:4]
            rows.append(ui.divider(f"{current_year} · {ui.usd(year_rev[current_year])}"))

        # Tren dibandingkan rata-rata harian bulan sebelumnya (adil untuk bulan berjalan).
        arrow = ui.trend(daily, prev_daily)
        prev_daily = daily

        name = ui.month_name(m_key, with_year=False) + ("*" if m_key == current_month else "")
        rows.append(ui.row(
            [name, str(agg["days"]), ui.num(agg["imp"]), ui.usd(cpm, 3), ui.usd(daily), ui.usd(agg["rev"])],
            ["", "", "", ui.CPM_COLOR, "", ui.REV_COLOR],
            arrow,
        ))

    total_cpm, total_daily = month_stats(total)
    bright = Style.BRIGHT
    total_row = ui.row(
        ["TOTAL", str(total["days"]), ui.num(total["imp"]), ui.usd(total_cpm, 3),
         ui.usd(total_daily), ui.usd(total["rev"])],
        [bright, bright, bright, ui.CPM_COLOR + bright, bright, ui.REV_COLOR],
    )

    print()
    ui.print_table(["BULAN", "HARI", "IMPRESI", "CPM", "RATA/HR", "REVENUE"],
                   rows, total_row, arrow_col=4)

    best = max(months, key=lambda m: monthly[m]["rev"])
    print()
    print(f" {Style.DIM}Bulan terbaik  {Style.RESET_ALL}{ui.month_name(best)} "
          f"{Fore.GREEN}{ui.usd(monthly[best]['rev'])}")
    ui.info("* bulan berjalan · ▲▼ rata/hari vs bulan lalu")
    print()

# ==============================================================================
# 4. MAIN
# ==============================================================================

if __name__ == "__main__":
    ui.title("ADSTERRA · SEMUA BULAN", f"Sejak {ui.month_name(Config.START_DATE_ALL_TIME[:7])}")

    client = AdsterraClient(Config.API_KEY)
    res = client.get_stats()

    if res:
        show_report(res)
