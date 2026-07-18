@echo off
cd /d "%~dp0"

git add .
git commit -m "actualizar streamlit"
git push

pause