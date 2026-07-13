
#!/bin/bash

set -e
echo ""
echo "🚀 Updating server..."

# Warna untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Konfigurasi FTP
FTP_HOST="103.235.75.18:66"
FTP_USER="haloka"
FTP_PASS="sb8LhCmBeWNXWe6F"
FTP_REMOTE_DIR="/"  # atau "/" untuk root
LOCAL_DIR="./dist"


# Fungsi untuk print dengan warna
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}


main () {
    print_status "Checking dist folder..."
    if [ -d "$LOCAL_DIR" ]; then
        print_status "dist folder exists"
    else
        print_error "dist folder does not exist, silakan run bun --bun run build atau npm run build"
        exit 1
    fi
    # Upload semua file dari folder dist
    lftp -c "
    open ftp://$FTP_USER:$FTP_PASS@$FTP_HOST
    set ftp:ssl-allow no
    mirror -R $LOCAL_DIR $FTP_REMOTE_DIR --verbose
    bye
    "

    rm -rf "$LOCAL_DIR"
}

main "$@"