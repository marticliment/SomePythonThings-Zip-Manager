#!/bin/bash
cd "$( dirname "$0" )"
cd zipmanager
rm -rf build dist
python3 -m PyInstaller --onefile "Darwin_minimal.spec"
