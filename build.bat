@echo off
REM Builds dist\AlfTorrent.exe. Requires Python 3.12 (64-bit) installed next to any other version.
py -3.12 -m pip install --upgrade pip
py -3.12 -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
  echo.
  echo Installation failed. Make sure 64-bit Python 3.12 is installed.
  pause
  exit /b 1
)
py -3.12 -m PyInstaller --noconsole --onefile --name AlfTorrent ^
  --icon AlfTorrent.ico --add-data "AlfTorrent.ico;." ^
  --collect-all libtorrent --collect-all customtkinter ^
  --hidden-import pystray._win32 app.py
echo.
echo Done: dist\AlfTorrent.exe
pause
