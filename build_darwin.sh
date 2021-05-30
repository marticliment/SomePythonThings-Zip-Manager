#!/bin/bash
cd "$( dirname "$0" )"
cd zipmanager
python3 -m PyInstaller "Darwin.spec" --windowed
cd dist/SomePythonThings\ Zip\ Manager.app/Contents/MacOS
sudo codesign --remove-signature "SomePythonThings Zip Manager"
echo
mv "SomePythonThings Zip Manager.app" ../../
