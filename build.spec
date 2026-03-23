# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files

_spec_path = Path(SPECPATH).resolve()
_project = _spec_path.parent
_main_script = _project / "src" / "main.py"
if not _main_script.is_file():
    _project = Path.cwd()
    _main_script = _project / "src" / "main.py"
if not _main_script.is_file():
    raise SystemExit(
        f"Cannot find src/main.py (SPECPATH={SPECPATH!r}, cwd={Path.cwd()!r})"
    )

_ct_datas = collect_data_files("customtkinter")
_font_datas = []
_font_dir = _project / "assets" / "fonts"
if _font_dir.is_dir():
    for f in _font_dir.iterdir():
        if f.is_file() and f.suffix.lower() in (".ttf", ".otf"):
            _font_datas.append((str(f), str(Path("assets") / "fonts")))

_icon_abs = (_project / "assets" / "icon.ico").resolve()
if not _icon_abs.is_file():
    raise SystemExit(f"Missing exe icon: {_icon_abs}")

a = Analysis(
    [str(_main_script)],
    pathex=[str(_project), str(_project / "src")],
    binaries=[],
    datas=_ct_datas + _font_datas,
    hiddenimports=["win32timezone"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "numpy",
        "numpy.libs",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="AutoClicker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(_icon_abs),
)
