@echo off
chcp 65001 > nul
echo =======================================================================
echo   DYNATSIMO — CONFIGURATION DE LA TÂCHE PLANIFIÉE AUTOMATIQUE WINDOWS
echo =======================================================================
echo.
echo Cette commande enregistre une tâche planifiée dans Windows pour exécuter
echo automatiquement la synchronisation CHIRPS / MODIS / GeoServer tous les jours.
echo.

set TASK_NAME=Dynatsimo_Auto_Sync_GeoServer
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%sync_pipeline.py

:: Recherche de python.exe
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Python n'a pas été trouvé dans le PATH.
    pause
    exit /b 1
)

for /f "delims=" %%i in ('where python') do set PYTHON_EXE=%%i & goto :found_python
:found_python

echo Python détecté : %PYTHON_EXE%
echo Script cible   : %PYTHON_SCRIPT%
echo.

:: Création de la tâche planifiée quotidienne à 03:00 du matin
schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%PYTHON_SCRIPT%\"" /sc daily /st 03:00 /f /rl HIGHEST

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================================
    echo  [SUCCÈS] La tâche planifiée '%TASK_NAME%' a été créée !
    echo  Elle s'exécutera automatiquement chaque jour à 03:00 en arrière-plan.
    echo =======================================================================
) else (
    echo.
    echo [ATTENTION] Veuillez exécuter ce fichier .bat en tant qu'Administrateur si l'accès est refusé.
)

echo.
pause
