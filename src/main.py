from __future__ import annotations

import queue
import sys
import threading
from pathlib import Path

# Running `python src\main.py` needs this folder on sys.path for sibling imports.
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from app_window import run_app  # noqa: E402
from clicker import clicker_worker  # noqa: E402
from state import AppState  # noqa: E402


def main() -> None:
    state = AppState()
    shutdown_event = threading.Event()
    ui_queue: queue.Queue[str] = queue.Queue()

    worker = threading.Thread(
        target=clicker_worker,
        args=(state, shutdown_event),
        name="clicker",
        daemon=True,
    )
    worker.start()

    run_app(state, shutdown_event, ui_queue)


if __name__ == "__main__":
    main()
