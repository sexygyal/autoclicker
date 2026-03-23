from __future__ import annotations

import queue
from typing import Callable

from pynput import keyboard

DEFAULT_START = "<f6>"
DEFAULT_STOP = "<f7>"
# pynput GlobalHotKeys: last key in a combo must be a single character (not "<e>").
DEFAULT_EXIT = "<ctrl>+<shift>+e"


def create_hotkey_listener(
    on_start: Callable[[], None],
    on_stop: Callable[[], None],
    on_exit: Callable[[], None],
    start_combo: str = DEFAULT_START,
    stop_combo: str = DEFAULT_STOP,
    exit_combo: str = DEFAULT_EXIT,
) -> keyboard.GlobalHotKeys:
    bindings = {
        start_combo: on_start,
        stop_combo: on_stop,
        exit_combo: on_exit,
    }
    hk = keyboard.GlobalHotKeys(bindings)
    hk.start()
    return hk


def pump_ui_queue(
    root,
    ui_queue: "queue.Queue[str]",
    handlers: dict[str, Callable[[], None]],
) -> None:
    while True:
        try:
            msg = ui_queue.get_nowait()
        except queue.Empty:
            break
        fn = handlers.get(msg)
        if fn:
            fn()
    root.after(80, lambda: pump_ui_queue(root, ui_queue, handlers))
