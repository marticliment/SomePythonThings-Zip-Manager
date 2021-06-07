#!/bin/bash
cd "$( dirname "$0" )"
cd zipmanager
rm -rf build dist
python3 -m PyInstaller --onefile "Darwin.spec"
cd dist/SomePythonThings\ Zip\ Manager.app/Contents/MacOS
sudo codesign --remove-signature "SomePythonThings Zip Manager"
cd ../../../
pwd
ls
echo
mv "SomePythonThings Zip Manager.app" ../../