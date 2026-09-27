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

if exist "chroma_db\chroma.sqlite3" (
    echo Chroma database already exists. Skipping policy knowledge base rebuild.
) else (
    echo Building the policy knowledge base...
    python build_knowledge_base.py
    if errorlevel 1 (
        echo Knowledge base build failed.
        exit /b 1
    )
)

exit /b 0
