rmdir /Q /S build
rmdir /Q /S dist
python -m PyInstaller "SomePythonThings Zip Manager.py" --add-data "background-zipmanager.jpg;." --add-data "icon-zipmanager.png;."  --icon icon.ico --hidden-import="pkg_resources.py2_warn" --exclude-module eel
pause