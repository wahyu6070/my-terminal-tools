#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
--------------------------------------------------------------------------------
Script: Adsterra Half-Month Tracker (v4.0)
Author: Wahyu Kurniawan
Date: 2026-02-23
Description: 
    Script khusus untuk memantau performa Adsterra dengan sistem split bulan:
    - Periode 1: Tanggal 1 s/d 15
    - Periode 2: Tanggal 16 s/d Akhir Bulan
    
    [LOGIKA WAKTU - Otomatis GMT]
    - Menampilkan ringkasan total dari "Periode Sebelumnya".
    - Menampilkan rincian harian untuk "Periode Saat Ini" (hingga kemarin).
    - Menampilkan performa "Hari Ini" secara terpisah karena data belum final.

Dependencies:
    - requests, tabulate, colorama
--------------------------------------------------------------------------------
"""

import sys
import json
import time
import requests
import calendar
from datetime import datetime, timedelta, timezone

# Cek kelengkapan library eksternal
try:
    from tabulate import tabulate
    from colorama import init, Fore, Style, Back
    # Inisialisasi colorama agar warna reset otomatis setelah dipanggil
    init(autoreset=True) 
except ImportError:
    print("Error: Library belum lengkap.")
    print("Silakan jalankan perintah berikut di terminal:")
    print("pip install tabulate colorama requests")
    sys.exit(1)

# ==============================================================================
# 1. KONFIGURASI (HALF-MONTH MODE)
# ==============================================================================

class Config:
    # Kredensial API Adsterra
    API_KEY = "d99b6eb88c389817b16af23dd030f280"
    BASE_URL = "https://api3.adsterratools.com/publisher/stats.json"
    USER_AGENT = "WahyuBot/4.0 (HalfMonthMode)"
    
    # Pengaturan Zona Waktu (GMT = UTC+0)
    # Sangat penting agar pergantian hari sesuai dengan server Adsterra (GMT)
    TZ_GMT = timezone(timedelta(hours=0))

# ==============================================================================
# 2. PENGELOLA WAKTU & PERIODE
# ==============================================================================

class TimeManager:
    """Kelas khusus untuk menangani logika pembagian tanggal 1-15 dan 16-Akhir Bulan"""
    
    def __init__(self):
        # Ambil waktu sekarang berdasarkan zona waktu GMT
        self.now = datetime.now(Config.TZ_GMT)
        self.today_date = self.now.date()
        
    def get_periods(self):
        """
        Menghitung batas tanggal untuk periode saat ini dan periode sebelumnya.
        Mengembalikan dictionary berisi objek datetime.date.
        """
        if self.today_date.day <= 15:
            # --- JIKA HARI INI TANGGAL 1 s/d 15 ---
            # Periode Saat Ini: Tanggal 1 s/d 15 bulan ini
            curr_start = self.today_date.replace(day=1)
            curr_end = self.today_date.replace(day=15)
            
            # Periode Sebelumnya: Tanggal 16 s/d akhir bulan lalu
            # Cari hari terakhir di bulan lalu dengan mundur 1 hari dari tanggal 1 bulan ini
            last_day_prev_month = curr_start - timedelta(days=1)
            prev_start = last_day_prev_month.replace(day=16)
            prev_end = last_day_prev_month
            
        else:
            # --- JIKA HARI INI TANGGAL 16 s/d AKHIR BULAN ---
            # Periode Saat Ini: Tanggal 16 s/d akhir bulan ini
            curr_start = self.today_date.replace(day=16)
            
            # Cari hari terakhir bulan ini menggunakan modul calendar
            _, last_day = calendar.monthrange(self.today_date.year, self.today_date.month)
            curr_end = self.today_date.replace(day=last_day)
            
            # Periode Sebelumnya: Tanggal 1 s/d 15 bulan ini
            prev_start = self.today_date.replace(day=1)
            prev_end = self.today_date.replace(day=15)
            
        return {
            "prev_start": prev_start,
            "prev_end": prev_end,
            "curr_start": curr_start,
            "curr_end": curr_end,
            "today": self.today_date
        }

# ==============================================================================
# 3. CLIENT API
# ==============================================================================

class AdsterraClient:
    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-Key": api_key,
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/json"
        })

    def get_stats(self, start_date_str, finish_date_str):
        """
        Mengambil data dari Adsterra berdasarkan rentang tanggal string (YYYY-MM-DD).
        """
        params = {
            "start_date": start_date_str,
            "finish_date": finish_date_str,
            "group_by": "date" 
        }

        print(f"{Fore.CYAN}[SYSTEM] Menghubungi Server Adsterra...")
        print(f"{Fore.CYAN}[SYSTEM] Rentang Tarik Data: {Fore.YELLOW}{start_date_str}{Fore.CYAN} s/d {Fore.YELLOW}{finish_date_str}")
        
        try:
            start_time = time.time()
            resp = self.session.get(Config.BASE_URL, params=params, timeout=30)
            duration = time.time() - start_time
            
            if resp.status_code == 200:
                print(f"{Fore.GREEN}[SUCCESS] Data diterima dalam {duration:.2f} detik.")
                return resp.json()
            else:
                print(f"{Fore.RED}[ERROR] HTTP Code: {resp.status_code}")
                print(f"{Fore.RED}[ERROR] Response: {resp.text}")
                return None
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}[CONN] Error: Koneksi Timeout (Lebih dari 30 detik).")
            return None
        except Exception as e:
            print(f"{Fore.RED}[CONN] Error: Terjadi kesalahan sistem -> {e}")
            return None

# ==============================================================================
# 4. PEMROSESAN & TAMPILAN LAPORAN
# ==============================================================================

class ReportFormatter:
    """Kelas untuk mengkategorikan data dan mencetak antarmuka CLI yang rapi"""
    
    @staticmethod
    def format_usd(val):
        return f"${float(val):,.3f}"

    @staticmethod
    def format_num(val):
        return f"{int(val):,}".replace(",", ".")

    @staticmethod
    def calculate_cpm(revenue, impression):
        """Menghindari error division by zero jika impression 0"""
        if impression <= 0:
            return 0.0
        return (revenue / impression) * 1000

    def process_and_show(self, raw_data, periods):
        if not raw_data or "items" not in raw_data:
            print(f"{Fore.RED}Data kosong atau gagal diakses dari API.")
            return

        items = raw_data["items"]
        
        # Penampung data untuk masing-masing kategori
        prev_data = []
        curr_data = []
        today_data = None

        # 4.1 Pemilahan Data berdasarkan Tanggal
        for item in items:
            date_str = item.get("date", "")
            if not date_str:
                continue
                
            try:
                # Parse string ke objek date untuk komparasi matematika
                item_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            # Klasifikasi ke keranjang yang sesuai
            if item_date == periods["today"]:
                today_data = item
            elif periods["prev_start"] <= item_date <= periods["prev_end"]:
                prev_data.append(item)
            elif periods["curr_start"] <= item_date < periods["today"]:
                curr_data.append(item)

        # 4.2 Menampilkan Laporan PERIODE SEBELUMNYA
        self._print_previous_period_summary(prev_data, periods)
        
        # 4.3 Menampilkan Laporan PERIODE SAAT INI (Hingga Kemarin)
        self._print_current_period_table(curr_data, periods)
        
        # 4.4 Menampilkan Laporan HARI INI
        self._print_today_live(today_data, periods)

    def _print_previous_period_summary(self, prev_data, periods):
        print("\n" + "="*55)
        print(f"{Back.MAGENTA}{Fore.WHITE} [1] RINGKASAN PERIODE SEBELUMNYA {Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}Rentang: {periods['prev_start'].strftime('%d %b %Y')} s/d {periods['prev_end'].strftime('%d %b %Y')}{Style.RESET_ALL}")
        print("="*55)
        
        if not prev_data:
            print(f"{Fore.LIGHTBLACK_EX}Tidak ada data untuk periode sebelumnya.")
            return

        tot_rev = sum(i.get("revenue", 0.0) for i in prev_data)
        tot_imp = sum(i.get("impression", 0) for i in prev_data)
        avg_cpm = self.calculate_cpm(tot_rev, tot_imp)
        hari_berjalan = len(prev_data)
        avg_daily = tot_rev / hari_berjalan if hari_berjalan > 0 else 0.0

        summary = [
            ["Total Impressions", self.format_num(tot_imp)],
            ["Rata-rata CPM", self.format_usd(avg_cpm)],
            ["Rata-rata Harian", self.format_usd(avg_daily)],
            ["TOTAL REVENUE", f"{Fore.GREEN}{Style.BRIGHT}{self.format_usd(tot_rev)}{Style.RESET_ALL}"]
        ]
        print(tabulate(summary, tablefmt="plain"))

    def _print_current_period_table(self, curr_data, periods):
        print("\n" + "="*55)
        print(f"{Back.BLUE}{Fore.WHITE} [2] RINCIAN PERIODE SAAT INI (Hingga Kemarin) {Style.RESET_ALL}")
        print(f"{Fore.BLUE}Rentang: {periods['curr_start'].strftime('%d %b %Y')} s/d (Maks Kemarin){Style.RESET_ALL}")
        print("="*55)

        if not curr_data:
            print(f"{Fore.LIGHTBLACK_EX}Belum ada data final untuk periode ini (Mungkin ini awal siklus).")
        else:
            # Urutkan tanggal Ascending
            curr_data = sorted(curr_data, key=lambda x: x.get('date', '0000-00-00'))
            
            table_data = []
            tot_rev = 0.0
            tot_imp = 0
            
            for item in curr_data:
                date_str = item.get("date", "-")
                imp = item.get("impression", 0)
                cpm = item.get("cpm", 0.0)
                rev = item.get("revenue", 0.0)

                tot_rev += rev
                tot_imp += imp

                # Logika Pewarnaan (Detail visual)
                rev_str = self.format_usd(rev)
                if rev > 12.0:
                    rev_str = f"{Fore.GREEN}{Style.BRIGHT}{rev_str}{Style.RESET_ALL}"
                elif rev > 0:
                    rev_str = f"{Fore.GREEN}{rev_str}{Style.RESET_ALL}"
                else:
                    rev_str = f"{Fore.LIGHTBLACK_EX}{rev_str}{Style.RESET_ALL}"
                
                cpm_str = self.format_usd(cpm)
                if cpm > 0.6:
                    cpm_str = f"{Fore.YELLOW}{cpm_str}{Style.RESET_ALL}"

                table_data.append([
                    date_str,
                    self.format_num(imp),
                    cpm_str,
                    rev_str
                ])

            headers = ["TANGGAL", "IMPRESSIONS", "CPM", "REVENUE"]
            print(tabulate(table_data, headers=headers, tablefmt="simple_grid", stralign="right"))

            # Menampilkan Ringkasan Periode Saat Ini
            avg_cpm = self.calculate_cpm(tot_rev, tot_imp)
            hari_berjalan = len(curr_data)
            avg_daily = tot_rev / hari_berjalan if hari_berjalan > 0 else 0.0

            print("\n--- ESTIMASI SEMENTARA PERIODE INI ---")
            curr_summary = [
                ["Total Impressions", self.format_num(tot_imp)],
                ["Rata-rata Harian", self.format_usd(avg_daily)],
                ["TOTAL REVENUE", f"{Fore.GREEN}{Style.BRIGHT}{self.format_usd(tot_rev)}{Style.RESET_ALL}"]
            ]
            print(tabulate(curr_summary, tablefmt="plain"))

    def _print_today_live(self, today_data, periods):
        print("\n" + "="*55)
        print(f"{Back.YELLOW}{Fore.BLACK}{Style.BRIGHT} [3] LIVE STATS HARI INI (Data Belum Final) {Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Tanggal: {periods['today'].strftime('%d %b %Y')} (GMT){Style.RESET_ALL}")
        print("="*55)
        
        if not today_data:
            print(f"{Fore.LIGHTBLACK_EX}Sistem Adsterra belum mencatat traffic untuk hari ini.")
        else:
            imp = today_data.get("impression", 0)
            cpm = today_data.get("cpm", 0.0)
            rev = today_data.get("revenue", 0.0)
            
            live_stats = [
                ["Impression Masuk", self.format_num(imp)],
                ["CPM Sementara", self.format_usd(cpm)],
                ["Revenue Terkumpul", f"{Fore.GREEN}{Style.BRIGHT}{self.format_usd(rev)}{Style.RESET_ALL}"]
            ]
            print(tabulate(live_stats, tablefmt="plain"))
        
        print("="*55 + "\n")

# ==============================================================================
# 5. EXECUTION BLOCK
# ==============================================================================

if __name__ == "__main__":
    # Header ASCII "HALF MONTH"
    print(f"\n{Fore.CYAN}{Style.BRIGHT}")
    print(r"  _   _    _    _     _____   __  __  ___  _   _ _____ _   _ ")
    print(r" | | | |  / \  | |   |  ___| |  \/  |/ _ \| \ | |_   _| | | |")
    print(r" | |_| | / _ \ | |   | |_    | |\/| | | | |  \| | | | | |_| |")
    print(r" |  _  |/ ___ \| |___|  _|   | |  | | |_| | |\  | | | |  _  |")
    print(r" |_| |_/_/   \_\_____|_|     |_|  |_|\___/|_| \_| |_| |_| |_|")
    print(f"{Style.RESET_ALL}")
    
    print(f"User   : Wahyu Kurniawan")
    print(f"Sistem : Siklus 15-Harian (Pisah Hari Ini - GMT)")
    print("-" * 61)
    
    # 1. Inisialisasi Pengelola Waktu
    time_mgr = TimeManager()
    periods = time_mgr.get_periods()
    
    # Karena kita ingin membandingkan periode sebelumnya dan saat ini,
    # kita tarik data dari API mulai dari 'prev_start' hingga 'today'.
    start_api_date = periods["prev_start"].strftime('%Y-%m-%d')
    finish_api_date = periods["today"].strftime('%Y-%m-%d')
    
    # 2. Inisialisasi Client dan Tarik Data
    client = AdsterraClient(Config.API_KEY)
    raw_data = client.get_stats(start_api_date, finish_api_date)
    
    # 3. Format dan Tampilkan
    if raw_data:
        formatter = ReportFormatter()
        formatter.process_and_show(raw_data, periods)
        