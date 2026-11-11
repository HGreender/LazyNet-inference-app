@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

"%SCRIPT_DIR%venv\Scripts\python.exe" "%SCRIPT_DIR%lazy_net_inference_app\main.py"

echo.
echo Код выхода: %errorlevel%
pause

endlocal