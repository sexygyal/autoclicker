from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class AppState:
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    running: bool = False
    self_hwnd: int | None = None
    interval_ms: int = 100
    jitter_ms: int = 0

    def snapshot(self) -> tuple[bool, int | None, int, int]:
        with self._lock:
            return (
                self.running,
                self.self_hwnd,
                self.interval_ms,
                self.jitter_ms,
            )

    def set_running(self, value: bool) -> None:
        with self._lock:
            self.running = value

    def set_self_hwnd(self, hwnd: int | None) -> None:
        with self._lock:
            self.self_hwnd = hwnd

    def set_timing(self, interval_ms: int, jitter_ms: int) -> None:
        with self._lock:
            self.interval_ms = max(1, int(interval_ms))
            self.jitter_ms = max(0, int(jitter_ms))
