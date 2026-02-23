#!/data/data/com.termux/files/usr/bin/bash

# ==============================================================================
# SCRIPT PENYIAPAN BIN TERMUX & PYTHON ENV (ISOLATED MODE)
# Description: Mengunduh script Python dari GitHub ke folder khusus (mypython),
#              membuat wrapper eksekusi (a, b, c, d, z) di folder bin,
#              serta mengunduh tools Git (p, push) dari GitHub.
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. KONFIGURASI DIREKTORI & URL REPOSITORY
# ------------------------------------------------------------------------------
BIN_DIR="$PREFIX/bin"
PYTHON_DIR="$PREFIX/mypython"

BASE_URL_PYTHON="https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/python"
BASE_URL_SCRIPT="https://raw.githubusercontent.com/wahyu6070/my-terminal-tools/main/script"

# Konfigurasi Warna Terminal
MERAH='\033[0;31m'
HIJAU='\033[0;32m'
BIRU='\033[0;36m'
KUNING='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BIRU}[*] Memulai Setup Environment Terisolasi Termux...${NC}"

# ------------------------------------------------------------------------------
# 2. MEMBUAT DIREKTORI KHUSUS PYTHON
# ------------------------------------------------------------------------------
echo -e "\n${KUNING}[1/4] Menyiapkan direktori khusus Python ($PYTHON_DIR)...${NC}"
if [ ! -d "$PYTHON_DIR" ]; then
    mkdir -p "$PYTHON_DIR"
    echo -e "${HIJAU} -> Direktori berhasil dibuat.${NC}"
else
    echo -e "${HIJAU} -> Direktori sudah ada, melanjutkan...${NC}"
fi

# ------------------------------------------------------------------------------
# 3. MENGUNDUH SCRIPT PYTHON DARI GITHUB KE /MYPYTHON
# ------------------------------------------------------------------------------
echo -e "\n${KUNING}[2/4] Mengunduh script Python Adsterra dari GitHub...${NC}"

download_python() {
    FILE_NAME=$1
    echo -e "${BIRU} -> Mengunduh: ${KUNING}$FILE_NAME${NC}"
    curl -sL "$BASE_URL_PYTHON/$FILE_NAME" -o "$PYTHON_DIR/$FILE_NAME"
}

download_python "cek_semua_data_adsterra_8_day.py"
download_python "cek_semua_data_adsterra_30_day.py"
download_python "cek_semua_data_adsterra_3_bulan.py"
download_python "cek_semua_data_adsterra.py"
download_python "z.py"

# ------------------------------------------------------------------------------
# 4. MEMBUAT WRAPPER EXECUTABLE (a, b, c, d, z) DI /BIN
# ------------------------------------------------------------------------------
echo -e "\n${KUNING}[3/4] Membuat executable command di Termux bin...${NC}"

# Fungsi untuk membuat wrapper yang bersih tanpa perintah 'cd'
create_wrapper() {
    CMD_NAME=$1
    PY_FILE=$2
    
    echo -e "${BIRU} -> Menulis perintah: ${KUNING}$CMD_NAME${NC}"
    cat << EOF > "$BIN_DIR/$CMD_NAME"
#!/data/data/com.termux/files/usr/bin/bash
# Auto-generated wrapper untuk $PY_FILE
python3 "$PYTHON_DIR/$PY_FILE" "\$@"
EOF
    chmod +x "$BIN_DIR/$CMD_NAME"
}

# Mapping perintah terminal ke file Python
create_wrapper "a" "cek_semua_data_adsterra_8_day.py"
create_wrapper "b" "cek_semua_data_adsterra_30_day.py"
create_wrapper "c" "cek_semua_data_adsterra_3_bulan.py"
create_wrapper "d" "cek_semua_data_adsterra.py"
create_wrapper "z" "z.py"

# ------------------------------------------------------------------------------
# 5. MENGUNDUH SCRIPT BASH (p & push) DARI GITHUB
# ------------------------------------------------------------------------------
echo -e "\n${KUNING}[4/4] Mengunduh bash script Git Automation...${NC}"

echo -e "${BIRU} -> Mengunduh 'p'...${NC}"
curl -sL "$BASE_URL_SCRIPT/p" -o "$BIN_DIR/p"
chmod +x "$BIN_DIR/p"

echo -e "${BIRU} -> Mengunduh 'push'...${NC}"
curl -sL "$BASE_URL_SCRIPT/push" -o "$BIN_DIR/push"
chmod +x "$BIN_DIR/push"

echo -e "${HIJAU} -> Selesai. Semua file bash siap digunakan.${NC}"

# ------------------------------------------------------------------------------
# 6. PENYELESAIAN
# ------------------------------------------------------------------------------
echo -e "\n=================================================="
echo -e "${HIJAU}✔ PROSES INSTALASI SELESAI DENGAN SEMPURNA!${NC}"
echo -e "=================================================="
echo -e "${BIRU}Arsitektur sistem saat ini:${NC}"
echo -e " - File Python Asli  : ${KUNING}$PYTHON_DIR${NC}"
echo -e " - Command Eksekusi  : ${KUNING}$BIN_DIR${NC}"
echo -e "\nAnda bisa langsung mengetik perintah berikut di mana saja:"
echo -e " - ${HIJAU}a${NC}    : Laporan 8 Hari"
echo -e " - ${HIJAU}b${NC}    : Laporan 30 Hari"
echo -e " - ${HIJAU}c${NC}    : Laporan 3 Bulan (90 Hari)"
echo -e " - ${HIJAU}d${NC}    : Laporan Seluruh Data (All-Time)"
echo -e " - ${HIJAU}z${NC}    : Laporan 15 Harian (Half-Month)"
echo -e " - ${HIJAU}p${NC}    : Git Auto Pull, Add, Commit & Push"
echo -e " - ${HIJAU}push${NC} : Smart Update Date (.md) & Git Push"
