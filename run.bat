@echo off

:: Always work from the folder containing this .bat file
cd /d "%~dp0"

:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    goto RunServer
)

:: Request administrative privileges
echo Requesting administrative privileges...
powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
exit /b


:RunServer

echo Administrative permissions confirmed.
echo Starting llama-server...
echo.

:: Launch llama-server in the background within this terminal
start "" /b ".\llama\llama-server.exe" -m ".\model\Qwen_Qwen3.5-4B-Q4_K_M.gguf" --jinja -fa on -ngl 99 -c 16384 --port 8000

:: Wait 2 seconds for server initialization before opening the browser
timeout /t 2 /nobreak >nul

:: Open browser link in default web browser
start "" "http://127.0.0.1:8000"

:: Keep the terminal window open to view server logs
pause >nul