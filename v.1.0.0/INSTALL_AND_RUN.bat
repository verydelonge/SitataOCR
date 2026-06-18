@echo off
title SitataOCR - Installer Terbaru (SourceForge)
echo ========================================
echo    SitataOCR - Full Installer (Fixed 2025)
echo ========================================
echo.

:: 1. Cek Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python tidak ditemukan!
    echo Silakan install dari: https://www.python.org/downloads/
    pause & exit
)
python --version
echo Python OK.

:: 2. Upgrade pip
echo [1/4] Upgrading pip...
python -m pip install --upgrade pip

:: 3. Install Libraries
echo [2/4] Installing Libraries...
pip install mss pillow psutil keyboard opencv-python ddddocr pytesseract easyocr customtkinter --no-warn-script-location
echo Installing heavy libraries...
pip install paddleocr torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

:: 4. Tesseract OCR (Pakai SourceForge - Lebih Stabil)
echo [3/4] Installing Tesseract OCR...
if exist "Tesseract-OCR\tesseract.exe" (
    echo ✓ Tesseract sudah terinstall.
    goto :launch
)

echo Downloading Tesseract from SourceForge...
set TESS_URL=https://sourceforge.net/projects/tesseract-ocr.mirror/files/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe/download
set TESS_FILE=%temp%\tesseract_setup.exe

:: Download dengan User-Agent (untuk menghindari block)
powershell -Command ^
"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%TESS_URL%' -OutFile '%TESS_FILE%' -TimeoutSec 120 -UserAgent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'"

if exist "%TESS_FILE%" (
    echo Installing Tesseract...
    start /wait %TESS_FILE% /S /D="%CD%\Tesseract-OCR"
    del %TESS_FILE% 2>nul
    echo ✓ Tesseract berhasil diinstall.
) else (
    echo.
    echo [ERROR] Download gagal secara otomatis.
    echo.
    echo Silakan download manual dari link berikut:
    echo https://sourceforge.net/projects/tesseract-ocr.mirror/files/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe
    echo.
    echo Kemudian install ke folder: %CD%\Tesseract-OCR
    echo.
    pause
)

:launch
:: 5. Jalankan Program
echo [4/4] Menjalankan SitataOCR...
if exist "launcher.pyw" (
    start pythonw launcher.pyw
) else (
    echo ERROR: launcher.pyw tidak ditemukan!
    pause
)

echo.
echo Installer selesai!
echo Jika muncul error library, jalankan file ini lagi.
timeout /t 5 >nul
