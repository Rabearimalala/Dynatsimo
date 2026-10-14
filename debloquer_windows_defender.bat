@echo off
chcp 65001 > nul
echo =======================================================================
echo   DYNATSIMO — DÉBLOCAGE DE LA SÉCURITÉ WINDOWS (DEFENDER)
echo =======================================================================
echo.

:: Vérification des droits administrateur
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Ce script a besoin des autorisations Administrateur.
    echo Une fenetre de confirmation Windows (UAC) va s'ouvrir...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

echo [1/2] Desactivation du "Dispositif d'acces controle aux dossiers"...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-MpPreference -EnableControlledFolderAccess Disabled"

echo [2/2] Ajout des autorisations pour Python et le dossier Dynatsimo...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Add-MpPreference -ControlledFolderAccessAllowedApplications 'C:\Users\Hanitriniala\AppData\Local\Programs\Python\Python312\python.exe', 'C:\Users\Hanitriniala\AppData\Local\Programs\Python\Python312\Scripts\earthengine.exe', 'C:\Windows\System32\cmd.exe', 'C:\Program Files\nodejs\node.exe'"

echo.
echo =======================================================================
echo  [SUCCES] Windows Defender ne bloquera plus vos traitements !
echo =======================================================================
echo.
pause
