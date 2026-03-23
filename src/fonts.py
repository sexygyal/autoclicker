from __future__ import annotations

import os
import sys
import tkinter
from pathlib import Path

UI_FONT_FAMILY = "MotivaSansUI"
UI_FONT_BOLD = "MotivaSansUIBold"
MONO_FONT_FAMILY = "Consolas"


def _base_dirs() -> list[Path]:
    dirs: list[Path] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        dirs.append(Path(meipass))
    dirs.append(Path(__file__).resolve().parent.parent)
    return dirs


def _assets_font_dir() -> Path | None:
    for base in _base_dirs():
        p = base / "assets" / "fonts"
        if p.is_dir():
            return p
    return None


def _steam_roots() -> list[Path]:
    roots: list[Path] = []
    for env in ("ProgramFiles", "ProgramFiles(x86)"):
        v = os.environ.get(env)
        if v:
            roots.append(Path(v) / "Steam")
    return roots


def _pick_from_dir(folder: Path) -> tuple[Path | None, Path | None]:
    names_regular = (
        "MotivaSans-Regular.ttf",
        "MotivaSansNormal.ttf",
        "MotivaSans.ttf",
    )
    names_bold = (
        "MotivaSans-Bold.ttf",
        "MotivaSansBold.ttf",
    )
    reg = next((folder / n for n in names_regular if (folder / n).is_file()), None)
    bold = next((folder / n for n in names_bold if (folder / n).is_file()), None)
    return reg, bold


def _steam_font_candidates(steam: Path) -> list[Path]:
    rels = (
        "steamui/resource/fonts",
        "clientui/fonts",
        "tenfoot/resource/fonts",
        "public/steamui/fonts",
    )
    out: list[Path] = []
    for rel in rels:
        d = steam / rel
        if not d.is_dir():
            continue
        try:
            for p in d.iterdir():
                if p.is_file() and p.suffix.lower() == ".ttf" and "motiva" in p.name.lower():
                    out.append(p)
        except OSError:
            continue
    return out


def _find_motiva_files() -> tuple[Path | None, Path | None]:
    ad = _assets_font_dir()
    if ad:
        reg, bold = _pick_from_dir(ad)
        if reg or bold:
            return reg or bold, bold or reg

    for steam in _steam_roots():
        if not steam.is_dir():
            continue
        motiva = _steam_font_candidates(steam)
        if not motiva:
            continue
        regular = next(
            (p for p in motiva if "bold" not in p.name.lower()),
            motiva[0],
        )
        bold = next((p for p in motiva if "bold" in p.name.lower()), None)
        return regular, bold or regular

    return None, None


def register_ui_fonts(tk_app: tkinter.Misc) -> tuple[str, str]:
    reg_path, bold_path = _find_motiva_files()
    fallback = ("Segoe UI", "Segoe UI")
    if not reg_path and not bold_path:
        return fallback
    try:
        if not (reg_path and reg_path.is_file()):
            return fallback
        tk_app.tk.call("font", "create", UI_FONT_FAMILY, "-file", str(reg_path))
        if bold_path and bold_path.is_file() and bold_path.resolve() != reg_path.resolve():
            tk_app.tk.call("font", "create", UI_FONT_BOLD, "-file", str(bold_path))
        else:
            tk_app.tk.call("font", "create", UI_FONT_BOLD, "-copy", UI_FONT_FAMILY)
        return UI_FONT_FAMILY, UI_FONT_BOLD
    except tkinter.TclError:
        return fallback
