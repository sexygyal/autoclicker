# AutoClicker

    AutoClicker is a Windows application that automatically left-clicks at
    the cursor, with user-controlled timing and global hotkeys.

    Copyright (C) 2026  Tanner Lucier

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.



##### Windows auto-clicker with a compact UI: timing, jitter, global hotkeys (F6 start, F7 stop, Ctrl+Shift+E exit)

---

## Minimum requirements

| Thing | Notes |
|--------|--------|
| **Windows 10 or 11, 64-bit** | 32-bit Windows won’t work. |
| **For the prebuilt .exe only** | [.NET 8 **Desktop** Runtime (x64)](https://dotnet.microsoft.com/en-us/download/dotnet/8.0) the “Desktop” one, not just the tiny ASP.NET bundle. If Windows complains when you double-click, install that and try again. |
| **For building from source** | [.NET 8 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/8.0) (includes what you need to compile). |

---

## Standalone .exe users (GitHub Releases)

1. Download **`AutoClickerLite.exe`** from the release.
2. Put it anywhere you like.
3. If the first launch fails with a missing-runtime message, install the **.NET 8 Desktop Runtime x64** from Microsoft (link in the table above), then double-click again.
4. No `setup.bat`, no Python, no pip. We did it boys

---

## Open source & building for a GitHub release

### What’s in this folder (what you actually need)

| Path | Why it exists |
|------|----------------|
| **`AutoClickerLiteDotnet/`** | Source: `Form1.cs`, `Program.cs`, `AutoClickerLiteDotnet.csproj`, **`icon.ico`** (don’t drop this, the build and taskbar icon expect it). |
| **`build.bat`** | Publishes two single-file framework-dependent exes (see below). |
| **`LICENSE`** | GPL v3, attach this so people know the deal. |

You do **not** need `bin/`, `obj/`, or `out-*` in git; they are build output. The **`out-safe`** and **`out-slim`** folders are created when you run `build.bat`.

### Build steps (maintainer / CI / your machine)

1. Install the **.NET 8 SDK** and clone/checkout this tree.
2. Open a terminal in **`v1.1.0-stable`** (the folder that contains `build.bat`).
3. Run **`build.bat`**.
4. When it finishes:
   - **`out-safe\AutoClickerLite.exe`** Standard Release single-file publish.
   - **`out-slim\AutoClickerLite.exe`** Same idea, a few flags stripped (no debug symbols, invariant globalization, etc.); usually slightly smaller.

Close any running copy of the app before building, or Windows may lock the exe in `out-slim` and the script will fail halfway, telling you cause it took me 3 hours to realize.

---

Made this to auto-click in Banana, unironically made something faster than OPAutoClicker (1 click per second faster). This still scratches the itch; future updates are “maybe” unless someone else wants the wheel. If you’re here from itch, the repo is [here, like right here, click here if you want it, get it?](https://github.com/sexygyal/autoclicker) Thank you <3
