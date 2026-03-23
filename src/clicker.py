from __future__ import annotations

import random
import threading
import time

from pynput.mouse import Button, Controller

from state import AppState
from windows import cursor_over_hwnd, is_window_handle_valid

_mouse = Controller()


def clicker_worker(state: AppState, shutdown_event: threading.Event) -> None:
    while not shutdown_event.is_set():
        running, self_hwnd, interval_ms, jitter_ms = state.snapshot()

        if not running:
            time.sleep(0.05)
            continue

        if self_hwnd and not is_window_handle_valid(self_hwnd):
            time.sleep(0.05)
            continue

        if cursor_over_hwnd(self_hwnd):
            time.sleep(0.02)
            continue

        try:
            _mouse.click(Button.left, 1)
        except Exception:
            pass

        extra = random.randint(0, jitter_ms) if jitter_ms else 0
        time.sleep(max(0.001, (interval_ms + extra) / 1000.0))
