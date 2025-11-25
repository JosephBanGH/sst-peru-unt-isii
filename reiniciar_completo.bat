@echo off
echo ========================================
echo REINICIO COMPLETO - Sistema SST
echo ========================================
echo.

echo Limpiando cache de Python...
powershell -Command "Get-ChildItem -Path '.\app' -Filter '*.pyc' -Recurse | Remove-Item -Force"
powershell -Command "Get-ChildItem -Path '.\app' -Filter '__pycache__' -Recurse -Directory | Remove-Item -Recurse -Force"

echo Limpiando cache de Streamlit...
powershell -Command "Remove-Item -Path '$env:USERPROFILE\.streamlit' -Recurse -Force -ErrorAction SilentlyContinue"
powershell -Command "if (Test-Path '.streamlit\cache') { Remove-Item -Path '.streamlit\cache' -Recurse -Force }"

echo.
echo Cache limpiado completamente!
echo.
echo Iniciando aplicacion...
echo.

call venv\Scripts\activate
streamlit run app/main.py

pause
