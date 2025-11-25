@echo off
echo ========================================
echo Sistema SST Peru - Ejecutar
echo ========================================
echo.

REM Verificar entorno virtual
if not exist venv\Scripts\activate.bat (
    echo ERROR: Entorno virtual no encontrado
    echo Ejecuta primero: instalar.bat
    pause
    exit /b 1
)

REM Verificar archivo .env
if not exist .env (
    echo ERROR: Archivo .env no encontrado
    echo Copia .env.example a .env y configura tus credenciales
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar aplicacion
echo Iniciando Sistema SST Peru...
echo.
echo La aplicacion se abrira en tu navegador
echo Presiona Ctrl+C para detener el servidor
echo.
streamlit run app/main.py

pause
