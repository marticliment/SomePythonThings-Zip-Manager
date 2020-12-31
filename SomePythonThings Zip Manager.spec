# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SomePythonThings Zip Manager.py'],
             pathex=['/home/marticlilop/Escriptori/SPTPrograms/_Zip with PySide2'],
             binaries=[],
             datas=[('background-zipmanager.png', '.'), ('black-zipmanager.png', '.'), ('icon-zipmanager.png', '.'), ('icons-zipmanager', 'icons-zipmanager')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='SomePythonThings Zip Manager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False , icon='icon.icns')
