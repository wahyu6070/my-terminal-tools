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
        [[ "$PLATFORM" == "Termux" ]] && echo "Jalankan: pkg install python curl" || echo "Jalankan: sudo apt install python3 python3-venv curl"
        exit 1
    }
done

PYTHON_DIR="$DATA_DIR/python"
TOOLS_DIR="$DATA_DIR/script"
VENV_DIR="$DATA_DIR/venv"
BASH_BIN="$(command -v bash)"
mkdir -p "$BIN_DIR" "$PYTHON_DIR" "$TOOLS_DIR"

echo "[*] Menyiapkan virtual environment Python ($PLATFORM)..."
[[ -x "$VENV_DIR/bin/python" ]] || "$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install requests tabulate colorama

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

create_wrapper a "$PYTHON_DIR/cek_semua_data_adsterra_8_day.py" "\"$VENV_DIR/bin/python\""
create_wrapper b "$PYTHON_DIR/cek_semua_data_adsterra_30_day.py" "\"$VENV_DIR/bin/python\""
create_wrapper c "$PYTHON_DIR/cek_semua_data_adsterra_3_bulan.py" "\"$VENV_DIR/bin/python\""
create_wrapper d "$PYTHON_DIR/cek_semua_data_adsterra.py" "\"$VENV_DIR/bin/python\""
create_wrapper z "$PYTHON_DIR/z.py" "\"$VENV_DIR/bin/python\""
create_wrapper p "$TOOLS_DIR/p" bash
create_wrapper push "$TOOLS_DIR/push" bash

echo "Selesai. Perintah tersedia: a, b, c, d, z, p, push"
echo "Command directory: $BIN_DIR"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Tambahkan ke PATH: echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.bashrc"
fi
