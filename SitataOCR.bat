@echo off
title SitataOCR - Launcher

echo ========================================
echo    SitataOCR - Starting Application
echo ========================================
echo.

:: ====================== CEK FILE ======================
if not exist "launcher.pyw" (
    echo [ERROR] File launcher.pyw tidak ditemukan!
    echo Pastikan anda menjalankan BAT ini di folder yang sama dengan launcher.pyw
    echo.
    pause
    exit /b
)

:: ====================== PRIORITAS 1: Python di folder saat ini ======================
if exist "pythonw.exe" (
    echo [1] Menjalankan dengan pythonw.exe lokal...
    start "" pythonw.exe launcher.pyw
    exit /b
)

if exist "runtime\pythonw.exe" (
    echo [1] Menjalankan dengan pythonw.exe dari folder runtime...
    start "" runtime\pythonw.exe launcher.pyw
    exit /b
)

:: ====================== PRIORITAS 2: Python dari PATH ======================
where pythonw.exe >nul 2>nul
if %errorlevel% equ 0 (
    echo [2] Menjalankan dengan pythonw dari PATH...
    start pythonw launcher.pyw
    exit /b
)

:: ====================== PRIORITAS 3: Cari di folder umum ======================
echo [3] Mencari Python di folder instalasi...

set "PYTHON_DIRS=%LOCALAPPDATA%\Programs\Python\Python313
%LOCALAPPDATA%\Programs\Python\Python312
%LOCALAPPDATA%\Programs\Python\Python311
%ProgramFiles%\Python313
%ProgramFiles%\Python312
%ProgramFiles%\Python311
%ProgramFiles(x86)%\Python313
%ProgramFiles(x86)%\Python312
%ProgramFiles(x86)%\Python311"

for %%d in (%PYTHON_DIRS%) do (
    if exist "%%d\pythonw.exe" (
        echo [SUCCESS] Ditemukan di: %%d
        start "" "%%d\pythonw.exe" launcher.pyw
        exit /b
    )
)

:: ====================== FALLBACK ======================
echo [4] Mencoba fallback dengan python.exe...
where python.exe >nul 2>nul
if %errorlevel% equ 0 (
    echo Menjalankan dengan python.exe (mungkin muncul console)...
    start python launcher.pyw
    exit /b
)

:: ====================== GAGAL ======================
echo.
echo [ERROR] Python tidak ditemukan!
echo.
echo Solusi:
echo 1. Install Python dari https://www.python.org/downloads/
echo 2. Centang "Add Python to PATH" saat instalasi
echo 3. Jalankan INSTALL_AND_RUN.bat sekali lagi
echo.
pause
exit /b