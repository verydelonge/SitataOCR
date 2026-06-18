# SitataOCR

SitataOCR adalah aplikasi desktop berbasis Python untuk membaca teks captcha (6 karakter alfanumerik) secara otomatis dengan dukungan multiple OCR engine (DdddOCR, Tesseract, EasyOCR, PaddleOCR). Aplikasi ini dirancang untuk kemudahan penggunaan dengan antarmuka gelap (dark theme) dan hotkey.

## ✨ Fitur Utama

- **Pilih area captcha** melalui drag & drop
- **Scan otomatis** dengan tombol ` (backtick) atau klik tombol Run
- **Multiple preprocessing** gambar (terang, adaptive threshold)
- **Menggabungkan hasil** dari 4 mesin OCR untuk akurasi maksimal
- **Auto-copy** hasil 6 karakter ke clipboard
- **Logging** aktivitas ke file `sitataOCR.log`

## 🚀 Cara Instalasi

1. Pastikan **Python 3.8+** sudah terinstal (Centang "Add Python to PATH").
2. Clone repository ini atau download semua file.
3. Jalankan **`INSTALL_AND_RUN.bat`** sebagai Administrator.
   - Script akan menginstall semua library Python (`pip install ...`)
   - Mengunduh dan menginstall **Tesseract OCR** dari SourceForge (ke folder `Tesseract-OCR`)
   - Menjalankan launcher yang akan memuat OCR engines.
4. Setelah splash selesai, aplikasi utama muncul.

> **Catatan:** Koneksi internet diperlukan saat instalasi untuk mengunduh library dan Tesseract.

## 🕹️ Cara Penggunaan

1. Klik tombol **🎯 Pilih Area** lalu drag untuk memilih area captcha di layar.
2. Tekan tombol **`** (backtick, biasanya di kiri angka 1) atau klik tombol **🚀 Run**.
3. Program akan mengambil screenshot area tersebut, memproses gambar, dan mencoba membaca teks.
4. Jika berhasil mendapatkan 6 karakter, hasil akan otomatis tersalin ke clipboard dan ditampilkan hijau.
5. Jika gagal, akan dicoba ulang hingga 2 kali.

## 🧩 Teknologi yang Digunakan

- **Python 3** + Tkinter / CustomTkinter
- **mss** (screenshot cepat)
- **OpenCV** (preprocessing gambar)
- **DdddOCR** (OCR berbasis deep learning, cepat)
- **Tesseract OCR** (open source OCR engine)
- **EasyOCR** & **PaddleOCR** (cadangan untuk akurasi tinggi)

## 📁 Struktur File

| File | Deskripsi |
|------|------------|
| `INSTALL_AND_RUN.bat` | Installer satu klik (pip + Tesseract + jalankan) |
| `SitataOCR.bat` | Launcher alternatif yang mencari Python di berbagai lokasi |
| `launcher.pyw` | Launcher dengan GUI kecil (ngecek library, Tesseract, lalu jalankan main app) |
| `sitataOCR.pyw` | Aplikasi utama (UI + OCR logic) |
| `captcha_region.json` | Menyimpan area pilihan user (auto dibuat) |
| `sitataOCR.log` | File log aktivitas |

## ⚠️ Catatan Penting

- Aplikasi ini hanya berjalan di **Windows** (karena menggunakan Tesseract.exe dan path khusus).
- Jika Tesseract tidak terinstall otomatis, Anda bisa download manual dari [SourceForge](https://sourceforge.net/projects/tesseract-ocr.mirror/files/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe) dan install ke folder `Tesseract-OCR` di direktori proyek.
- Untuk pengembang: pastikan menjalankan `launcher.pyw` atau `sitataOCR.pyw` setelah menginstall semua dependencies.

## 📄 Lisensi

Proyek ini bersifat open source. Silakan gunakan, modifikasi, dan distribusikan.

## 👤 Author

Dibuat oleh [verydelonge](https://github.com/verydelonge)
