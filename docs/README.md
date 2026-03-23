# AutoClicker

    AutoClicker is a python tool that automatically left-clicks any user 
    given position on the screen, for any user-set amount of time

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



##### Windows auto-clicker with a simple UI: timing, global hotkeys (F6 start, F7 stop, Ctrl+Shift+E exit), priority window, and it won’t click while your cursor is over the app.

---

## Minimum requirements

| Thing | Notes |
|--------|--------|
| **Windows 10 or 11, 64-bit** | 32-bit Windows unfortunately won’t work. |
| **Python 3.10 or newer** | From [python.org](https://www.python.org/downloads/). During install, turn on **“Add python.exe to PATH”**. |
| **Internet (first time only)** | So `setup.bat` can download packages. |

---

#### If you just plan on running the .exe version, you can take the .exe file out of this repo and place it anywhere, it will safely work. If you miss dependencies, loading up for the first time may take a while.

---
## Install dependencies

1. Double-click **`setup.bat`** in the project folder.  
2. Wait until it says it’s done.

If it says Python wasn’t found, reinstall Python and enable **Add to PATH**, then run `setup.bat` again.

---

## Run the app

In that same folder, open Command Prompt / PowerShell and run:

```bat
python src\main.py
```

---

## Build your .exe

If you've made any changes to the code and would like an .exe version (which any sane person would), unless there are new dependencies just double click `build.bat`

Your executable will be in **`dist\AutoClicker.exe`**.

---

Made this to Auto Click in Banana, unironically made something faster than OPAutoClicker (1 click per second faster). However this scratches my itch so future updates will most likely not happen unless other collaboraters would like to takeover the project

