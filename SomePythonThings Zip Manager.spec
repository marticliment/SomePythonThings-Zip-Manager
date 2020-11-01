# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SomePythonThings Zip Manager.py'],
             pathex=['E:\\Users\\Martí Climent\\SPTPrograms\\_Zip with PyQt5'],
             binaries=[],
             datas=[('background-zipmanager.png', '.'), ('icon-zipmanager.png', '.'), ('black-zipmanager.png', '.')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['eel', 'tkinter'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SomePythonThings Zip Manager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SomePythonThings Zip Manager')
