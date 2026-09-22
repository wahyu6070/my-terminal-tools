#!/usr/bin/env bash
# Installer My Terminal Tools untuk Termux dan Ubuntu/Debian.
set -euo pipefail

BASE_URL="https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main"

if [[ -n "${TERMUX_VERSION:-}" || "${PREFIX:-}" == /data/data/com.termux/files/usr* ]]; then
    PLATFORM="Termux"
    BIN_DIR="$PREFIX/bin"
    DATA_DIR="$PREFIX/mypython"
    PYTHON_BIN="python"
elif [[ -r /etc/os-release ]] && . /etc/os-release && [[ "${ID:-}" == "ubuntu" || " ${ID_LIKE:-} " == *" debian "* ]]; then
    PLATFORM="Ubuntu/Debian"
    BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
    DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/my-terminal-tools"
    PYTHON_BIN="python3"
else
    echo "ERROR: Installer hanya mendukung Termux dan Ubuntu/Debian." >&2
    exit 1
fi

for command in curl "$PYTHON_BIN"; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "ERROR: '$command' belum tersedia." >&2
        [[ "$PLATFORM" == "Termux" ]] && echo "Jalankan: pkg install python curl" || echo "Jalankan: sudo apt install python3 curl"
        exit 1
    }
done

PYTHON_DIR="$DATA_DIR/python"
TOOLS_DIR="$DATA_DIR/script"
BASH_BIN="$(command -v bash)"
PYTHON_EXECUTABLE="$(command -v "$PYTHON_BIN")"
mkdir -p "$BIN_DIR" "$PYTHON_DIR" "$TOOLS_DIR"

echo "[*] Menyiapkan dependensi Python global ($PLATFORM)..."
if [[ "$PLATFORM" == "Termux" ]]; then
    "$PYTHON_EXECUTABLE" -m pip install --upgrade requests tabulate colorama
elif ! "$PYTHON_EXECUTABLE" -c 'import requests, tabulate, colorama' >/dev/null 2>&1; then
    packages=(python3-requests python3-tabulate python3-colorama)
    if [[ ${EUID:-$(id -u)} -eq 0 ]]; then
        apt-get update
        apt-get install -y "${packages[@]}"
    elif command -v sudo >/dev/null 2>&1; then
        sudo apt-get update
        sudo apt-get install -y "${packages[@]}"
    else
        echo "ERROR: Dependensi Python belum tersedia." >&2
        echo "Jalankan sebagai root: apt install ${packages[*]}" >&2
        exit 1
    fi
fi

if ! "$PYTHON_EXECUTABLE" -c 'import requests, tabulate, colorama' >/dev/null 2>&1; then
    echo "ERROR: requests, tabulate, atau colorama belum dapat diimpor oleh $PYTHON_EXECUTABLE." >&2
    exit 1
fi

download() {
    local source="$1" destination="$2"
    echo " -> $(basename "$destination")"
    curl --fail --silent --show-error --location "$source" --output "$destination"
}

echo "[*] Mengunduh script Python..."
for file in adsterra_api.py cek_semua_data_adsterra_8_day.py cek_semua_data_adsterra_30_day.py cek_semua_data_adsterra_3_bulan.py cek_semua_data_adsterra.py z.py; do
    download "$BASE_URL/python/$file" "$PYTHON_DIR/$file"
done
echo "[*] Mengunduh script Git..."
download "$BASE_URL/script/p" "$TOOLS_DIR/p"
download "$BASE_URL/script/push" "$TOOLS_DIR/push"
download "$BASE_URL/script/update-lastmod" "$TOOLS_DIR/update-lastmod"

create_wrapper() {
    local name="$1" target="$2" interpreter="$3"
    cat > "$BIN_DIR/$name" <<EOF
#!$BASH_BIN
exec $interpreter "$target" "\$@"
EOF
    chmod +x "$BIN_DIR/$name"
}

create_wrapper a "$PYTHON_DIR/cek_semua_data_adsterra_8_day.py" "\"$PYTHON_EXECUTABLE\""
create_wrapper b "$PYTHON_DIR/cek_semua_data_adsterra_30_day.py" "\"$PYTHON_EXECUTABLE\""
create_wrapper c "$PYTHON_DIR/cek_semua_data_adsterra_3_bulan.py" "\"$PYTHON_EXECUTABLE\""
create_wrapper d "$PYTHON_DIR/cek_semua_data_adsterra.py" "\"$PYTHON_EXECUTABLE\""
create_wrapper z "$PYTHON_DIR/z.py" "\"$PYTHON_EXECUTABLE\""
create_wrapper p "$TOOLS_DIR/p" bash
create_wrapper push "$TOOLS_DIR/push" bash

echo "Selesai. Perintah tersedia: a, b, c, d, z, p, push"
echo "Command directory: $BIN_DIR"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Tambahkan ke PATH: echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.bashrc"
fi
