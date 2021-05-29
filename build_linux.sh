#!/bin/bash
cd zipmanager
python3 -m PyInstaller "Linux.spec"
cd dist
mv "SomePythonThings Zip Manager" "somepythonthings-zip-manager"
mv "somepythonthings-zip-manager" ../../
