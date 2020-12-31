#!/bin/bash
cd "$( dirname "$0" )"
python3.7 -m PyInstaller --noconfirm "SomePythonThings Zip Manager.py" --add-data "background-zipmanager.png":.  --add-data "black-zipmanager.png:."  --add-data "icon-zipmanager.png:." --icon icon.icns --hidden-import="pkg_resources.py2_warn" --windowed --add-data "icons-zipmanager:icons-zipmanager" --exclude-module PyQt5
cd dist/SomePythonThings\ Zip\ Manager.app/Contents/MacOS
sudo codesign --remove-signature "Python"