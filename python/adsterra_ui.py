#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Komponen tampilan terminal bersama untuk laporan Adsterra (command a, b, c).
Tabel dibuat ringkas tanpa garis per baris agar muat di layar Termux.
"""

from datetime import datetime
from colorama import Fore, Style

BULAN = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]
HARI = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
GAP = "  "

HEADER_COLOR = Fore.CYAN + Style.BRIGHT
CPM_COLOR = Fore.YELLOW
REV_COLOR = Fore.GREEN + Style.BRIGHT


def usd(val, decimals=2):
    return f"${float(val):,.{decimals}f}"


def num(val):
    return f"{int(val):,}".replace(",", ".")


def month_name(month_key, with_year=True):
    """'2026-02' -> 'Februari 2026' (atau 'Februari')."""
    try:
        dt = datetime.strptime(month_key, "%Y-%m")
    except ValueError:
        return month_key
    name = BULAN[dt.month - 1]
    return f"{name} {dt.year}" if with_year else name


def day_label(date_str):
    """'2026-09-24' -> 'Kam 24 Sep'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return date_str
    return f"{HARI[dt.weekday()]} {dt.day:02d} {BULAN[dt.month - 1][:3]}"


def trend(current, previous):
    """Panah naik/turun dibandingkan nilai sebelumnya."""
    if previous is None or current == previous:
        return (" ", "")
    return ("▲", Fore.GREEN) if current > previous else ("▼", Fore.RED)


def title(text, subtitle=None):
    print()
    print(f" {Fore.MAGENTA}{Style.BRIGHT}{text}")
    if subtitle:
        print(f" {Style.DIM}{subtitle}")


def info(text):
    print(f" {Style.DIM}{text}")


def error(text):
    print(f" {Fore.RED}{text}")


def fetch_ok(label, duration):
    print(f" {Style.DIM}{label}{Style.RESET_ALL} {Fore.GREEN}OK{Style.RESET_ALL} {Style.DIM}{duration:.1f}s")


def row(cols, colors=None, arrow=None):
    return {"cols": cols, "colors": colors, "arrow": arrow}


def divider(label):
    return {"divider": label}


def print_table(headers, rows, total=None, arrow_col=None):
    """
    Cetak tabel: kolom pertama rata kiri, sisanya rata kanan.
    rows berisi row(...) atau divider(...); arrow_col menaruh panah tren setelah kolom itu.
    """
    lines = [headers] + [r["cols"] for r in rows if "cols" in r]
    if total:
        lines.append(total["cols"])
    widths = [max(len(line[i]) for line in lines) for i in range(len(headers))]
    width = sum(widths) + len(GAP) * (len(widths) - 1) + (1 if arrow_col is not None else 0)

    def render(item):
        colors = item.get("colors") or [""] * len(item["cols"])
        parts = []
        for i, text in enumerate(item["cols"]):
            cell = text.ljust(widths[i]) if i == 0 else text.rjust(widths[i])
            if colors[i]:
                cell = f"{colors[i]}{cell}{Style.RESET_ALL}"
            if i == arrow_col:
                arrow, color = item.get("arrow") or (" ", "")
                cell += f"{color}{arrow}{Style.RESET_ALL}" if color else arrow
            parts.append(cell)
        return " " + GAP.join(parts)

    print(render(row(headers, [HEADER_COLOR] * len(headers))))
    for item in rows:
        if "divider" in item:
            label = f"── {item['divider']} "
            print(f" {Style.DIM}{label}{'─' * max(0, width - len(label))}")
        else:
            print(render(item))
    if total:
        print(f" {Style.DIM}{'─' * width}")
        print(render(total))


def print_daily_report(items):
    """Laporan harian (dipakai command a dan b)."""
    items = sorted(items, key=lambda x: x.get("date", "0000-00-00"))
    if not items:
        info("Tidak ada data pada periode ini.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    rows = []
    total_imp = 0
    total_rev = 0.0
    prev_rev = None
    current_month = None

    for item in items:
        date = item.get("date", "-")
        imp = int(item.get("impression", 0))
        cpm = float(item.get("cpm", 0.0))
        rev = float(item.get("revenue", 0.0))
        total_imp += imp
        total_rev += rev

        if date[:7] != current_month:
            current_month = date[:7]
            rows.append(divider(month_name(current_month)))

        is_today = date == today
        # Hari ini belum lengkap, jadi tidak diberi panah tren.
        arrow = (" ", "") if is_today else trend(rev, prev_rev)
        prev_rev = rev
        rows.append(row(
            [day_label(date) + ("*" if is_today else ""), num(imp), usd(cpm, 3), usd(rev)],
            ["", "", CPM_COLOR, REV_COLOR if rev > 0 else Style.DIM],
            arrow,
        ))

    total_cpm = (total_rev / total_imp * 1000) if total_imp > 0 else 0
    total = row(["TOTAL", num(total_imp), usd(total_cpm, 3), usd(total_rev)],
                [Style.BRIGHT, Style.BRIGHT, CPM_COLOR + Style.BRIGHT, REV_COLOR])

    print()
    print_table(["TANGGAL", "IMPRESI", "CPM", "REVENUE"], rows, total, arrow_col=3)

    full_days = [i for i in items if i.get("date") != today] or items
    avg = sum(float(i.get("revenue", 0.0)) for i in full_days) / len(full_days)
    best = max(full_days, key=lambda i: float(i.get("revenue", 0.0)))
    print()
    print(f" {Style.DIM}Rata-rata/hari {Style.RESET_ALL}{Fore.GREEN}{usd(avg)}"
          f"{Style.RESET_ALL} {Style.DIM}({len(full_days)} hari penuh)")
    print(f" {Style.DIM}Hari terbaik   {Style.RESET_ALL}{day_label(best.get('date', '-'))} "
          f"{Fore.GREEN}{usd(best.get('revenue', 0.0))}")
    info("* hari ini (belum lengkap) · ▲▼ vs hari sebelumnya")
    print()
