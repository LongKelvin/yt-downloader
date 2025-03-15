@echo off
setlocal enabledelayedexpansion

:: Check if PyInstaller is installed
where pyinstaller >nul 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller is not installed.
    set /p INSTALL_PYINSTALLER="Do you want to install PyInstaller? (Y/N): "
    if /I "%INSTALL_PYINSTALLER%"=="Y" (
        echo Installing PyInstaller...
        python -m pip install pyinstaller
        if %errorlevel% neq 0 (
            echo Failed to install PyInstaller. Exiting...
            exit /b 1
        )
    ) else (
        echo PyInstaller is required. Exiting...
        exit /b 1
    )
)

:: Ask user for the executable name
set /p EXE_NAME="Enter the name of the executable (default: yt_downloader_v0.2): "
if "%EXE_NAME%"=="" set EXE_NAME=yt_downloader_v0.2

:: Ask user for additional hidden imports
set /p HIDDEN_IMPORTS="Enter additional hidden imports (comma-separated, or leave blank): "

:: Run Python script to find qtawesome fonts path
for /f "delims=" %%i in ('python -c "import qtawesome, os; print(os.path.join(os.path.dirname(qtawesome.__file__), 'fonts', '*.ttf'))"') do set QTAWESOME_FONTS=%%i

:: Check if the fonts path was found
if "%QTAWESOME_FONTS%"=="" (
    echo Error: Could not find qtawesome fonts path.
    exit /b 1
)

:: Find the latest user guide and developer documentation
set USER_GUIDE=
set DEV_GUIDE=

for /f "delims=" %%F in ('python -c "import os, glob; files = sorted(glob.glob('docs/yt_downloader_user_guide_v*.pdf'), reverse=True); print(files[0] if files else '')"') do set USER_GUIDE=%%F
for /f "delims=" %%F in ('python -c "import os, glob; files = sorted(glob.glob('docs/yt_downloader_dev_documentation_v*.pdf'), reverse=True); print(files[0] if files else '')"') do set DEV_GUIDE=%%F

:: Build the PyInstaller command
set CMD=pyinstaller --onefile --windowed --name "%EXE_NAME%" main.py --hidden-import qtawesome --add-data "%QTAWESOME_FONTS%;qtawesome/fonts"

:: Add user-provided hidden imports
if not "%HIDDEN_IMPORTS%"=="" set CMD=%CMD% --hidden-import %HIDDEN_IMPORTS%

:: Include configs and docs folders
if exist configs set CMD=%CMD% --add-data "configs;configs"
if exist docs set CMD=%CMD% --add-data "docs;docs"

:: Include latest user guide and developer documentation if found
if not "%USER_GUIDE%"=="" set CMD=%CMD% --add-data "%USER_GUIDE%;docs"
if not "%DEV_GUIDE%"=="" set CMD=%CMD% --add-data "%DEV_GUIDE%;docs"

:: Execute PyInstaller
echo Running: %CMD%
%CMD%

endlocal
