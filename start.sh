#!/data/data/com.termux/files/usr/bin/bash

# ==================================================
# REMOTE INSTALLER - MY TERMINAL TOOLS
# Repo: github.com/wahyu6070/my-terminal-tools
# ==================================================

# Konfigurasi Warna
HIJAU='\033[0;32m'
BIRU='\033[0;36m'
NC='\033[0m'

BASE_URL="https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/script"
TARGET_DIR="$PREFIX/bin"

echo -e "${BIRU}[*] Memulai instalasi tools...${NC}"

# Fungsi download helper
download_tool() {
    TOOL_NAME=$1
    echo -e "${HIJAU} -> Mengunduh: $TOOL_NAME${NC}"
    
    # Download menggunakan curl (lebih silent) ke target dir
    curl -sL "$BASE_URL/$TOOL_NAME" -o "$TARGET_DIR/$TOOL_NAME"
    
    # Beri izin eksekusi
    chmod +x "$TARGET_DIR/$TOOL_NAME"
}

# 1. Install tool 'p' (Git lazy push)
download_tool "p"

# 2. Install tool 'push' (Hugo smart deploy)
download_tool "push"

echo -e "${BIRU}[*] Instalasi Selesai!${NC}"
echo -e "Coba ketik perintah: ${HIJAU}p${NC} atau ${HIJAU}push${NC}"

