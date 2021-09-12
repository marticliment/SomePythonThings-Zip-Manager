#!/bin/bash
cd /users/marticlilop/SPTPrograms/SomePythonThings-Zip-Manager/zipmanager
cd zipmanager
pwd
rm -rf build dist
python3 -m PyInstaller --onefile "./Darwin.spec"
cd dist/SomePythonThings\ Zip\ Manager.app/Contents/MacOS
sudo codesign --remove-signature "SomePythonThings Zip Manager"
cd ../../../
pwd
ls
echo
mv "SomePythonThings Zip Manager.app" ../../