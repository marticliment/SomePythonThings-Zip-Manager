#!/bin/bash
python3 -m PyInstaller --noconfirm "SomePythonThings Zip Manager.py" --add-data "background-zipmanager.jpg:." --add-data "icon-zipmanager.png:." --icon icon.icns --hidden-import="pkg_resources.py2_warn" --windowed --onefile
