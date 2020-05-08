# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['fs_main.py'],
             pathex=['D:\\SVN\\FourSeasons_reStructure\\main'],
             binaries=[('CHIPS510.dll', '.'),('drvISP.dll', '.'),
						('libapical_REN_AC_085.dll', '.'),('ISP510.dll', '.'),
						('IMR510.dll', '.')
						],
             datas=[],
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
          upx=False,
          runtime_tmpdir=None,
          console=True )
