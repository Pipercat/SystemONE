#!/bin/bash
set -e

# SmartSortierer Pro - NAS Folder Structure Initialization
# Creates the required folder structure for document workflow

NAS_ROOT="${SS_STORAGE_ROOT:-$HOME/mnt/nas/smartsortierer}"

echo "=== SmartSortierer Pro - Folder Initialization ==="
echo "NAS Root: $NAS_ROOT"
echo ""

# Create folders
mkdir -p "$NAS_ROOT"/{00_inbox,01_ingested,02_staging,03_sorted,04_archive,99_errors}
mkdir -p "$NAS_ROOT/02_staging/.locks"

# Set permissions (if needed)
chmod -R 755 "$NAS_ROOT"

echo "✓ Folder structure created:"
ls -la "$NAS_ROOT"

echo ""
echo "=== DONE ==="
