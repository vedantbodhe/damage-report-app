#!/usr/bin/env bash
# .platform/hooks/prebuild/01_install_system_packages.sh

# Enable EPEL repository
dnf install -y epel-release

# Install Tesseract + English and German language packs, plus zbar
dnf install -y \
    tesseract \
    tesseract-langpack-eng \
    tesseract-langpack-deu \
    zbar \
    zbar-devel

# Create symlink so pytesseract can find it
ln -sf /usr/bin/tesseract /usr/local/bin/tesseract || true