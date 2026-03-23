from __future__ import annotations

import ctypes
import queue
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from typing import Callable

import customtkinter as ctk

import fonts
import hotkeys
from state import AppState
from windows import cursor_over_hwnd, is_window_handle_valid, root_hwnd

ACCENT = "#1a9fff"
IDLE_DOT = "#e8a849"
BLOCKED_DOT = "#d8574e"
RUNNING_DOT = "#5ea454"
CARD = "#1e2329"
BG = "#171a21"
CHROME_BTN_FG = "#2a2f3a"
TITLEBAR_VPAD = 4
CHROME_BTN_W = 27
CHROME_BTN_H = 22
CHROME_BTN_FONT = 15
CHROME_BTN_RADIUS = 3
TITLEBAR_TEXT_PX = 13


def _format_hotkey_display(combo: str) -> str:
    return combo.replace("<", "").replace(">", "").replace("+", " + ")


class AutoClickerApp(ctk.CTk):
    def __init__(
        self,
        state: AppState,
        shutdown_event: threading.Event,
        ui_queue: queue.Queue[str],
    ) -> None:
        super().__init__()
        self._state = state
        self._shutdown_event = shutdown_event
        self._ui_queue = ui_queue
        self._hk = None
        self._drag_dx = 0
        self._drag_dy = 0

        self.title("AutoClicker")
        self.geometry("272x420")
        self.minsize(240, 360)
        self.configure(fg_color=BG)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        fam, fam_bold = fonts.register_ui_fonts(self)
        self._font_main = (fam, 12)
        self._font_bold = (fam_bold, 16)
        self._font_mono = (fonts.MONO_FONT_FAMILY, 11)

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.after(200, self._capture_self_hwnd)
        self.after(120, self._poll_status)
        self.after(1, self._start_hotkeys)

    def _start_hotkeys(self) -> None:
        q = self._ui_queue
        hotkeys.pump_ui_queue(
            self,
            q,
            {
                "start": self._handle_start_hotkey,
                "stop": self._handle_stop_hotkey,
                "exit": self._handle_exit_hotkey,
            },
        )
        self._hk = hotkeys.create_hotkey_listener(
            on_start=lambda: q.put("start"),
            on_stop=lambda: q.put("stop"),
            on_exit=lambda: q.put("exit"),
        )

    def _handle_start_hotkey(self) -> None:
        self._state.set_running(True)
        self._apply_timing_from_ui()

    def _handle_stop_hotkey(self) -> None:
        self._state.set_running(False)

    def _handle_exit_hotkey(self) -> None:
        self._on_close()

    def _on_close(self) -> None:
        self._state.set_running(False)
        self._shutdown_event.set()
        if self._hk is not None:
            try:
                self._hk.stop()
            except Exception:
                pass
        self.destroy()
        sys.exit(0)

    def _minimize_window(self) -> None:
        try:
            self.iconify()
        except Exception:
            try:
                hwnd = root_hwnd(int(self.winfo_id()))
                if hwnd:
                    ctypes.windll.user32.ShowWindow(hwnd, 6)
            except Exception:
                pass

    def _drag_start(self, event: object) -> None:
        self._drag_dx = event.x_root - self.winfo_rootx()  # type: ignore[attr-defined]
        self._drag_dy = event.y_root - self.winfo_rooty()  # type: ignore[attr-defined]

    def _drag_motion(self, event: object) -> None:
        x = event.x_root - self._drag_dx  # type: ignore[attr-defined]
        y = event.y_root - self._drag_dy  # type: ignore[attr-defined]
        self.geometry(f"+{x}+{y}")

    def _bind_drag(self, widget: tk.Misc) -> None:
        widget.bind("<Button-1>", self._drag_start)
        widget.bind("<B1-Motion>", self._drag_motion)

    def _chrome_button(
        self, parent: ctk.CTk | ctk.CTkFrame | tk.Frame, text: str, command: Callable[[], None]
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            width=CHROME_BTN_W,
            height=CHROME_BTN_H,
            command=command,
            fg_color=CHROME_BTN_FG,
            hover_color=ACCENT,
            text_color="#e5eef5",
            font=ctk.CTkFont(family=self._font_main[0], size=CHROME_BTN_FONT),
            corner_radius=CHROME_BTN_RADIUS,
            border_width=0,
        )

    def _capture_self_hwnd(self) -> None:
        self.update_idletasks()
        try:
            h = int(self.winfo_id())
            self._state.set_self_hwnd(root_hwnd(h))
        except Exception:
            self._state.set_self_hwnd(None)

    def _build_titlebar(self) -> None:
        vb = TITLEBAR_VPAD
        bar_h = CHROME_BTN_H + 2 * vb + 8  # extra headroom for CTk chrome buttons
        bar = tk.Frame(self, bg=CARD, height=bar_h, highlightthickness=0)
        bar.grid(row=0, column=0, sticky="ew")
        bar.grid_propagate(False)
        bar.grid_columnconfigure(0, weight=1)

        left = tk.Frame(bar, bg=CARD, highlightthickness=0, cursor="hand2")
        left.grid(row=0, column=0, sticky="nsew", padx=(8, 2), pady=0)
        left.grid_columnconfigure(1, weight=1)

        title_lbl = tk.Label(
            left,
            text="Auto Clicker",
            fg=ACCENT,
            bg=CARD,
            font=(self._font_bold[0], TITLEBAR_TEXT_PX, "bold"),
            anchor="w",
        )
        title_lbl.grid(row=0, column=0, sticky="nw", padx=0, pady=vb)
        filler = tk.Frame(left, bg=CARD, cursor="hand2", height=1)
        filler.grid(row=0, column=1, sticky="nsew")
        self._bind_drag(left)
        self._bind_drag(filler)
        self._bind_drag(title_lbl)

        min_btn = self._chrome_button(bar, "_", self._minimize_window)
        min_btn.grid(row=0, column=1, padx=(0, 3), pady=vb, sticky="ne")
        close_btn = self._chrome_button(bar, "×", self._on_close)
        close_btn.grid(row=0, column=2, padx=(0, 6), pady=vb, sticky="ne")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)

        self._build_titlebar()

        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        card.grid(row=1, column=0, sticky="ew", padx=10, pady=(6, 4))
        card.grid_columnconfigure(0, weight=1)

        self._build_timing_section(card, 0)
        self._build_hotkey_section(card, 1)

        status_frame = ctk.CTkFrame(self, fg_color=CARD, corner_radius=10)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 8))
        status_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            status_frame,
            text="Status",
            font=ctk.CTkFont(family=self._font_bold[0], size=13, weight="bold"),
            text_color="#c7d5e0",
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(6, 2))

        status_row = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_row.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
        self._status_dot = ctk.CTkFrame(
            status_row,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=IDLE_DOT,
        )
        self._status_dot.grid(row=0, column=0, padx=(0, 8), pady=0)
        self._status_dot.grid_propagate(False)
        self._status_word = ctk.CTkLabel(
            status_row,
            text="Idle",
            font=ctk.CTkFont(family=self._font_main[0], size=13, weight="bold"),
            text_color="#e5eef5",
            anchor="w",
        )
        self._status_word.grid(row=0, column=1, sticky="w")

    def _ms_entry_row(
        self,
        wrap: ctk.CTkFrame,
        grid_row: int,
        label: str,
        default: str,
        *,
        label_pady: tuple[int, int] = (0, 0),
        entry_pady: tuple[int, int] = (0, 0),
    ) -> ctk.CTkEntry:
        ctk.CTkLabel(
            wrap,
            text=label,
            font=ctk.CTkFont(family=self._font_main[0], size=12),
            text_color="#8f98a0",
        ).grid(row=grid_row, column=0, sticky="w", pady=label_pady)
        entry = ctk.CTkEntry(
            wrap,
            width=70,
            font=ctk.CTkFont(family=self._font_mono[0], size=12),
        )
        entry.insert(0, default)
        entry.grid(row=grid_row, column=1, sticky="w", padx=(8, 0), pady=entry_pady)
        return entry

    def _build_timing_section(self, parent: ctk.CTkFrame, row: int) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.grid(row=row, column=0, sticky="ew", padx=10, pady=(8, 3))
        wrap.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            wrap,
            text="Timing",
            font=ctk.CTkFont(family=self._font_bold[0], size=13, weight="bold"),
            text_color="#c7d5e0",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        self._interval_entry = self._ms_entry_row(wrap, 1, "Interval (ms)", "100")
        self._jitter_entry = self._ms_entry_row(
            wrap, 2, "Jitter max (ms)", "0", label_pady=(6, 0), entry_pady=(6, 0)
        )

        ctk.CTkButton(
            wrap,
            text="Apply",
            command=self._apply_timing_from_ui,
            fg_color="#2a475e",
            hover_color=ACCENT,
            font=ctk.CTkFont(family=self._font_main[0], size=12),
            height=28,
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def _build_hotkey_section(self, parent: ctk.CTkFrame, row: int) -> None:
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.grid(row=row, column=0, sticky="ew", padx=10, pady=(3, 8))

        ctk.CTkLabel(
            wrap,
            text="Global hotkeys",
            font=ctk.CTkFont(family=self._font_bold[0], size=13, weight="bold"),
            text_color="#c7d5e0",
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))

        rows = [
            ("Start clicking", hotkeys.DEFAULT_START),
            ("Stop clicking", hotkeys.DEFAULT_STOP),
            ("Exit app", hotkeys.DEFAULT_EXIT),
        ]
        for i, (label, combo) in enumerate(rows, start=1):
            ctk.CTkLabel(
                wrap,
                text=label,
                font=ctk.CTkFont(family=self._font_main[0], size=12),
                text_color="#8f98a0",
            ).grid(row=i, column=0, sticky="w", pady=1)
            ctk.CTkLabel(
                wrap,
                text=_format_hotkey_display(combo),
                font=ctk.CTkFont(family=self._font_mono[0], size=12),
                text_color="#e5eef5",
            ).grid(row=i, column=1, sticky="w", padx=(10, 0), pady=1)

    def _apply_timing_from_ui(self) -> None:
        try:
            interval = int(self._interval_entry.get().strip())
            jitter = int(self._jitter_entry.get().strip())
        except ValueError:
            messagebox.showwarning("Timing", "Use whole numbers (ms).", parent=self)
            return
        self._state.set_timing(interval, jitter)

    def _poll_status(self) -> None:
        running, self_hwnd, _, _ = self._state.snapshot()

        if not running or not self_hwnd or not is_window_handle_valid(self_hwnd):
            self._status_dot.configure(fg_color=IDLE_DOT)
            self._status_word.configure(text="Idle")
        elif cursor_over_hwnd(self_hwnd):
            self._status_dot.configure(fg_color=BLOCKED_DOT)
            self._status_word.configure(text="Blocked")
        else:
            self._status_dot.configure(fg_color=RUNNING_DOT)
            self._status_word.configure(text="Running")

        self.after(120, self._poll_status)


def run_app(state: AppState, shutdown_event: threading.Event, ui_queue: queue.Queue[str]) -> None:
    app = AutoClickerApp(state, shutdown_event, ui_queue)
    app.mainloop()
