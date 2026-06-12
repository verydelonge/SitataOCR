# ==================== CHECK PYTHON VERSIONS ====================
# Script ini untuk mengecek semua versi dependencies di sistem Anda

Write-Host "================================" -ForegroundColor Cyan
Write-Host "SITATA OCR - DEPENDENCY CHECKER" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python Version
Write-Host "[1] Python Version:" -ForegroundColor Yellow
python --version
Write-Host ""

# Check installed packages
Write-Host "[2] Checking Installed Packages..." -ForegroundColor Yellow
Write-Host ""

$packages = @(
    "customtkinter",
    "tkinter",
    "mss",
    "opencv-python",
    "pillow",
    "ddddocr",
    "pytesseract",
    "easyocr",
    "paddleocr",
    "keyboard",
    "numpy",
    "pyinstaller"
)

foreach ($pkg in $packages) {
    try {
        $version = python -m pip show $pkg | Select-String "Version:"
        if ($version) {
            Write-Host "$pkg : $version" -ForegroundColor Green
        } else {
            Write-Host "$pkg : ❌ NOT INSTALLED" -ForegroundColor Red
        }
    } catch {
        Write-Host "$pkg : ❌ ERROR CHECKING" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[3] Generating requirements.txt..." -ForegroundColor Yellow
pip freeze > requirements_current.txt
Write-Host "✅ Saved to: requirements_current.txt" -ForegroundColor Green

Write-Host ""
Write-Host "[4] Checking Tesseract Installation..." -ForegroundColor Yellow
$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:USERPROFILE\Tesseract-OCR\tesseract.exe"
)

$found = $false
foreach ($path in $tesseractPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Found: $path" -ForegroundColor Green
        & $path --version
        $found = $true
    }
}

if (-not $found) {
    Write-Host "❌ Tesseract-OCR NOT FOUND - Will need to bundle or install separately" -ForegroundColor Red
}

Write-Host ""
Write-Host "[5] Checking System Info..." -ForegroundColor Yellow
systeminfo | Select-String "OS Name", "System Manufacturer"

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "CHECK COMPLETE!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
