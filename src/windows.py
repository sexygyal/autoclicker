from __future__ import annotations

import ctypes

import win32api
import win32gui

user32 = ctypes.WinDLL("user32", use_last_error=True)
GA_ROOT = 2
GetAncestor = user32.GetAncestor
GetAncestor.argtypes = (ctypes.c_void_p, ctypes.c_uint)
GetAncestor.restype = ctypes.c_void_p


def root_hwnd(hwnd: int) -> int:
    if not hwnd:
        return 0
    root = GetAncestor(ctypes.c_void_p(hwnd), GA_ROOT)
    return int(root) if root else int(hwnd)


def get_cursor_pos() -> tuple[int, int]:
    x, y = win32api.GetCursorPos()
    return int(x), int(y)


def cursor_in_window_rect(hwnd: int, x: int, y: int) -> bool:
    if not hwnd or not is_window_handle_valid(hwnd):
        return False
    try:
        left, top, right, bottom = win32gui.GetWindowRect(int(hwnd))
    except Exception:
        return False
    # RECT right/bottom are exclusive.
    return left <= x < right and top <= y < bottom


def cursor_over_hwnd(hwnd: int | None) -> bool:
    if not hwnd:
        return False
    x, y = get_cursor_pos()
    return cursor_in_window_rect(hwnd, x, y)


def is_window_handle_valid(hwnd: int) -> bool:
    if not hwnd:
        return False
    try:
        return bool(win32gui.IsWindow(hwnd))
    except Exception:
        return False
