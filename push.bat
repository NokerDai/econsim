@echo off
cd /d "%~dp0"

set /p mensaje=Escribí el mensaje del commit:

echo === git add ===
git add .
pause

echo === git commit ===
git commit -m "%mensaje%"
pause

echo === git push ===
git push
pause