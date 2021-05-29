# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import importlib, os

package_imports = [['qtmodern', ['resources/frameless.qss', 'resources/style.qss']]]



a = Analysis(['__init__.py'],
             pathex=['/mnt/c/Users/marti/SPTPrograms/_Zip 4.0 with PySide2/zipmanager'],
             binaries=[('Compressor.py', '.'), ('Extractor.py', '.'), ('CustomWidgets.py', '.'), ('MainWindow.py', '.'), ('Tools.py', '.'), ('Updater.py', '.'), ('Welcome.py', '.')],
             datas=[('res', 'res')],
             hiddenimports=['pkg_resources.py2_warn', ".Tools.*", "json", "darkdetect", "qtmodern", "qt_thread_updater", "wget", "PySide2.*", "zipfile", "threading", "PySide2"],
             hookspath=[],
             runtime_hooks=[],
             excludes=['eel', 'tkinter', "PyQt5"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

a.datas += [('./qtmodern/resources/frameless.qss', f'/mnt/c/Users/marti/AppData/Local/Programs/Python/Python38/Lib/site-packages/qtmodern/resources/frameless.qss', "DATA")]
a.datas += [('./qtmodern/resources/style.qss', f'/mnt/c/Users/marti/AppData/Local/Programs/Python/Python38/Lib/site-packages/qtmodern/resources/style.qss', "DATA")]


#a.datas += [('.\\qtmodern\\resources\\frameless.qss', f'{os.path.expanduser("~")}\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\qtmodern\\resources\\frameless.qss', "DATA")]
#a.datas += [('.\\qtmodern\\resources\\style.qss', f'{os.path.expanduser("~")}\\AppData\\Local\\Programs\\Python\\Python38-32\\Lib\\site-packages\\qtmodern\\resources\\style.qss', "DATA")]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SomePythonThings Zip Manager',
          icon="res/icon.ico",
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
