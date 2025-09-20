@echo off
REM Gyors teszt script XTTS v2 Magyar TTS-hez
REM Quick test script for XTTS v2 Hungarian TTS

echo XTTS v2 Magyar TTS - Gyors Teszt
echo ================================

REM Aktiváljuk a virtual environment-et
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment aktiválása...
    call venv\Scripts\activate.bat
) else (
    echo Figyelem: Virtual environment nem található. Futtassa setup.bat-ot először.
    pause
    exit /b 1
)

REM Ellenőrizzük, hogy vannak-e referencia fájlok
set ref_count=0
for %%f in (example_voice_*.wav) do set /a ref_count+=1

if %ref_count%==0 (
    echo.
    echo Hiba: Nincsenek referencia hangfájlok!
    echo Kérem, készítsen example_voice_1.wav, example_voice_2.wav fájlokat
    echo ^(6-12 másodperc, 24kHz, mono formátumban^)
    echo.
    pause
    exit /b 1
)

echo Talált referencia fájlok: %ref_count% darab

REM Tesztek futtatása
echo.
echo 1. Alapvető teszt
python xtts_hungarian_tts.py --text "Jó reggelt! Ez egy teszt." --refs example_voice_1.wav --out test_basic.wav

if %errorlevel% neq 0 (
    echo Hiba az alapvető tesztnél!
    pause
    exit /b 1
)

echo.
echo 2. Többreferenciás teszt MP3 kimenettel
python xtts_hungarian_tts.py --text "Köszönöm a figyelmet, szép napot!" --refs example_voice_1.wav --refs example_voice_2.wav --out test_multi.wav --mp3

if %errorlevel% neq 0 (
    echo Hiba a többreferenciás tesztnél!
    pause
    exit /b 1
)

echo.
echo 3. Finomhangolt paraméterekkel
python xtts_hungarian_tts.py --text "A mesterséges intelligencia forradalmasítja a beszédtechnológiát." --refs example_voice_1.wav --out test_advanced.wav --temperature 0.6 --gpt-cond-len 8 --mp3

if %errorlevel% neq 0 (
    echo Hiba a finomhangolt tesztnél!
    pause
    exit /b 1
)

echo.
echo ================================
echo ✅ Minden teszt sikeresen lefutott!
echo.
echo Létrehozott fájlok:
for %%f in (test_*.wav test_*.mp3) do echo   - %%f
echo.
echo Tesztelje a hangfájlokat, és ellenőrizze a minőséget.
echo ================================
pause