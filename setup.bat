@echo off

REM Python control
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadi. python.org adresinden Python 3.10+ yukle.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] %%i

REM Virtual environment
if not exist "venv" (
    echo [*] Virtual environment olusturuluyor...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM API key file
if not exist "config\api_keys.json" (
    copy "config\api_keys.example.json" "config\api_keys.json" >nul
    echo [*] config\api_keys.json olusturuldu - Gemini API anahtarini buraya gir
)

echo [*] Paketler yukleniyor...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

REM Install fonts to Windows Fonts directory (admin rights may be required)
if exist "Fonts" (
    echo [*] Grift fontlari kuruluyor...
    for %%f in (Fonts\*.ttf) do (
        copy "%%f" "%WINDIR%\Fonts\" >nul 2>&1
    )
    echo [OK] Fontlar kuruldu (basarisiz olursa Fonts klasorunden elle yukle)
)

echo.
echo ================================
echo    Kurulum Tamamlandi!
echo ================================
echo.
echo JARVIS'i baslatmak icin:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
set /p choice="Simdi baslatilsin mi? (e/h): "
if /i "%choice%"=="e" start "" /MIN cmd /c "call venv\Scripts\activate.bat && python main.py"
exit /b 0
