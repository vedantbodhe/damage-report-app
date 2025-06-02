#!/usr/bin/env bash
dnf install -y tesseract tesseract-langpack-eng tesseract-langpack-deu zbar zbar-devel \
  libjpeg-turbo-devel libpng-devel freetype-devel libtiff-devel libwebp-devel

ln -sf /usr/bin/tesseract /usr/local/bin/tesseract || true