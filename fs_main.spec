# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['D:\\SVN\\FourSeasons_reStructure\\main\\fs_main.py'],
             pathex=['D:\\SVN'],
             binaries=[],
             datas=[('D:\\SVN\\FourSeasons_reStructure\\main\\dlls\\Chips2.dll', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='fs_main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
