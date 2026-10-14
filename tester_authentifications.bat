@echo off
chcp 65001 > nul
echo =======================================================================
echo   DYNATSIMO — TEST DE TOUTES LES AUTHENTIFICATIONS
echo =======================================================================
echo.

set PATH=C:\Program Files\nodejs;C:\Users\Hanitriniala\AppData\Local\Programs\Python\Python312;C:\Users\Hanitriniala\AppData\Local\Programs\Python\Python312\Scripts;C:\Program Files\PostgreSQL\10\bin;%PATH%

python scripts/test_authentications.py

echo.
pause
