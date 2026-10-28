@echo off
title FLEXEditor Website Manager
cd /d "%~dp0"
py manager.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python failed or was not found. Trying python...
    python manager.py
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Please make sure Python is installed.
    pause
)
