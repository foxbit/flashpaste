#!/bin/bash
set -e

# Config
APP_NAME="io.github.angelorosa.flashpaste"
VERSION="0.1.6"
DEB_NAME="flashpaste_${VERSION}_all"
BUILD_DIR="build_deb"

echo "Cleanup..."
rm -rf $DEB_NAME $DEB_NAME.deb $BUILD_DIR

echo "Creating directories..."
mkdir -p $DEB_NAME/DEBIAN

echo "Building with Meson..."
meson setup $BUILD_DIR --prefix=/usr
meson install -C $BUILD_DIR --destdir ../$DEB_NAME

echo "Copying control file..."
cp packaging/control $DEB_NAME/DEBIAN/

echo "Building .deb package..."
dpkg-deb --build $DEB_NAME

echo "Success! Package created: ${DEB_NAME}.deb"
echo "To install run: sudo apt install ./$DEB_NAME.deb"
