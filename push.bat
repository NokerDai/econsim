@echo off
cd /d "%~dp0"

set /p mensaje=Escribí el mensaje del commit: 

git add .
git commit -m "%mensaje%"
git push