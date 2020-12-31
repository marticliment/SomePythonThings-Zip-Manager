rmdir /Q /S build
rmdir /Q /S dist
python -m PyInstaller "SomePythonThings Zip Manager.py" --add-data "background-zipmanager.png;." --add-data "icon-zipmanager.png;."  --add-data "black-zipmanager.png;." --icon icon.ico --noconsole --hidden-import="pkg_resources.py2_warn" --exclude-module eel --exclude-module tkinter --exclude-module PyQt5 --add-data "icons-zipmanager;icons-zipmanager"
pause