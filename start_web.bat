@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Сначала создайте .venv и установите зависимости по README.md.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" manage.py migrate
if errorlevel 1 (
    pause
    exit /b 1
)
echo Откройте http://127.0.0.1:8000/ в браузере.
echo Для остановки сервера нажмите Ctrl+C.
".venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
pause
