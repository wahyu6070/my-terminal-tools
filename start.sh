#!/data/data/com.termux/files/usr/bin/bash

# ==================================================
# REMOTE INSTALLER - MY TERMINAL TOOLS
# Repo: github.com/wahyu6070/my-terminal-tools
# ==================================================

# 1. Konfigurasi Warna
HIJAU='\033[0;32m'
BIRU='\033[0;36m'
KUNING='\033[1;33m'
NC='\033[0m'

BASE_URL="https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/script"
TARGET_DIR="$PREFIX/bin"

echo -e "${BIRU}[*] Memulai Setup Environment Termux...${NC}"

# 2. Update & Upgrade System
# Menggunakan 'yes' agar tidak tanya konfirmasi y/n terus menerus
echo -e "${KUNING}[1/3] Melakukan Update System...${NC}"
pkg update -y && pkg upgrade -y

# 3. Install Paket Pilihan
# Catatan: 'ssh' di Termux paketnya bernama 'openssh'
# 'python3' di Termux biasanya paketnya 'python'
PKGS="hugo golang python git openssh file wget curl"

echo -e "${KUNING}[2/3] Menginstall Paket: $PKGS ...${NC}"
pkg install $PKGS -y

# 4. Download Custom Tools (p & push)
echo -e "${KUNING}[3/3] Mengunduh Custom Tools...${NC}"

download_tool() {
    TOOL_NAME=$1
    echo -e "${HIJAU} -> Menginstall: $TOOL_NAME${NC}"
    curl -sL "$BASE_URL/$TOOL_NAME" -o "$TARGET_DIR/$TOOL_NAME"
    chmod +x "$TARGET_DIR/$TOOL_NAME"
}

download_tool "p"
download_tool "push"
download_tool "a"
download_tool "b"
download_tool "c"
download_tool "d"

echo -e "${BIRU}=========================================${NC}"
echo -e "${HIJAU}✔ SETUP SELESAI! SEMUA SIAP DIGUNAKAN.${NC}"
echo -e "${BIRU}=========================================${NC}"
echo -e "Coba ketik: ${KUNING}hugo version${NC} atau ${KUNING}p${NC}"
