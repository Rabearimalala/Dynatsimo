@echo off
chcp 65001 > nul
echo =======================================================================
echo   DYNATSIMO — PROGRAMMATION HEBDOMADAIRE (CHAQUE LUNDI A 23:00)
echo =======================================================================
echo.

set TASK_NAME=Dynatsimo_Hebdomadaire_Lundi_23h
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%sync_pipeline.py

:: Recherche du chemin absolu de python.exe
for /f "delims=" %%i in ('where python') do set PYTHON_EXE=%%i & goto :found_python
:found_python

echo Executable Python : %PYTHON_EXE%
echo Script Pipeline   : %PYTHON_SCRIPT%
echo Frequence         : Chaque Lundi a 23:00
echo.

:: Creation de la tache planifiee dans Windows (Chaque Lundi / MON a 23:00)
schtasks /create /tn "%TASK_NAME%" /tr "\"%PYTHON_EXE%\" \"%PYTHON_SCRIPT%\"" /sc weekly /d MON /st 23:00 /f /rl HIGHEST

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================================
    echo  [SUCCES] La tache planifiee '%TASK_NAME%' est enregistree !
    echo.
    echo  Fonctionnement :
    echo  - Chaque Lundi soir a 23:00 precises, Windows executera automatiquement :
    echo    1. Le telechargement des nouveaux rasters CHIRPS et MODIS
    echo    2. La mise a jour de PostgreSQL / PostGIS (statistiques communales)
    echo    3. La publication des nouveaux GeoTIFFs dans GeoServer (donnees_dynatsimo)
    echo    4. L'actualisation des donnees et dates pour la carte React
    echo.
    echo  Le Mardi matin, l'application est prete et a jour sans aucune action !
    echo =======================================================================
) else (
    echo.
    echo [ATTENTION] Veuillez executer ce fichier .bat en tant qu'Administrateur (Clic droit - Executer en tant qu'administrateur).
)

echo.
pause
