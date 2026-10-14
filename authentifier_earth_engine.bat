@echo off
chcp 65001 > nul
echo =======================================================================
echo   DYNATSIMO — AUTHENTIFICATION GOOGLE EARTH ENGINE (%USERNAME%)
echo =======================================================================


set PATH=C:\Program Files\nodejs;C:\Users\Hanitriniala\AppData\Local\Programs\Python\Python312;C:\Users\Hanitriniala\AppData\Local\Programs\Python\Python312\Scripts;%PATH%

earthengine authenticate

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================================
    echo  [SUCCES] Votre compte Google Earth Engine est active et authentifie !
    echo =======================================================================
) else (
    echo.
    echo [ATTENTION] L'authentification a echoue ou a ete annulee.
)

echo.
pause
