del "SomePythonThings Zip Manager.exe"
cd zipmanager
rmdir /Q /S build
rmdir /Q /S dist
python -m PyInstaller "Win.spec"
cd dist
move "SomePythonThings Zip Manager.exe" ../../
cd ..
rmdir /Q /S build
rmdir /Q /S dist
