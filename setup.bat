@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
    echo Python was not found on PATH.
    echo Install Python 3.10+ and try again.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo Creating virtual environment...
    py -3 -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Installing Python requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if not exist ".env" if exist ".env.example" (
    copy ".env.example" ".env"
    echo Created .env from template.
)

if not exist "model" mkdir "model"
if not exist "model\.gitkeep" type NUL > "model\.gitkeep"

if not exist "llama\llama-server.exe" (
    echo.
    echo WARNING: llama-server.exe was not found in llama\.
    echo Download or place the llama.cpp server binary there before running the app.
)

echo.
echo Setup complete.
echo Next steps:
    echo   1. Put your GGUF model in the model folder.
    echo   2. Run run.bat to start the local LLM server.
    echo   3. Run python src\llm_client.py to test the client.
pause
