"""Pemulihan token API Adsterra dari sumber cadangan yang ditentukan pengguna."""

import re
from pathlib import Path
from typing import Optional

import requests

API_SOURCE = "https://winlator.me/adstera.txt"
TOKEN_PATTERN = re.compile(r"^\s*api\s*:\s*([A-Za-z0-9_-]{16,})\s*$", re.MULTILINE)


def _cache_path() -> Path:
    """Simpan token per-user, bukan di direktori instalasi yang dibagikan."""
    path = Path.home() / ".config" / "my-terminal-tools" / "adsterra_api_key"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def refresh_api_key() -> Optional[str]:
    """Ambil dan validasi field ``api : TOKEN`` dari sumber cadangan."""
    try:
        response = requests.get(API_SOURCE, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"[API] Gagal mengambil token cadangan: {error}")
        return None

    match = TOKEN_PATTERN.search(response.text)
    if not match:
        print("[API] Format token di sumber cadangan tidak valid.")
        return None

    token = match.group(1)
    cache = _cache_path()
    cache.write_text(token + "\n", encoding="utf-8")
    cache.chmod(0o600)
    print("[API] Token diperbarui dari winlator.me/adstera.txt.")
    return token


def get_cached_api_key(fallback: str) -> str:
    """Pakai token tersimpan jika tersedia; token bawaan tetap menjadi fallback."""
    try:
        token = _cache_path().read_text(encoding="utf-8").strip()
        return token or fallback
    except OSError:
        return fallback


def _is_auth_failure(response: requests.Response) -> bool:
    """Deteksi penolakan token, termasuk error autentikasi yang dikirim sebagai JSON."""
    if response.status_code in (401, 403):
        return True
    if response.status_code != 200:
        return False
    try:
        body = response.json()
    except ValueError:
        return False
    message = str(body.get("errors", body.get("error", ""))).lower() if isinstance(body, dict) else ""
    return any(term in message for term in ("api key", "token", "auth", "unauthorized", "forbidden"))


def get_with_token_refresh(session: requests.Session, url: str, **kwargs: object) -> requests.Response:
    """Request sekali lagi dengan token baru bila server menolak autentikasi."""
    response = session.get(url, **kwargs)
    if not _is_auth_failure(response):
        return response

    print("[API] Token ditolak; mencoba memperbarui token otomatis...")
    token = refresh_api_key()
    if not token:
        return response

    session.headers["X-API-Key"] = token
    return session.get(url, **kwargs)
