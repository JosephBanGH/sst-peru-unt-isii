@echo off
echo ========================================
echo Sistema SST Peru - Instalador
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    echo Por favor instala Python 3.8 o superior desde python.org
    pause
    exit /b 1
)

echo [1/5] Python detectado correctamente
echo.

REM Crear entorno virtual
echo [2/5] Creando entorno virtual...
python -m venv venv
if errorlevel 1 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)
echo Entorno virtual creado
echo.

REM Activar entorno virtual
echo [3/5] Activando entorno virtual...
call venv\Scripts\activate.bat
echo.

REM Instalar dependencias
echo [4/5] Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo Dependencias instaladas correctamente
echo.

REM Verificar archivo .env
echo [5/5] Verificando configuracion...
if not exist .env (
    echo ADVERTENCIA: Archivo .env no encontrado
    echo Copiando .env.example a .env
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env con tus credenciales antes de ejecutar
    echo.
)

echo.
echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo Proximos pasos:
echo 1. Edita el archivo .env con tus credenciales de Supabase y n8n
echo 2. Ejecuta: ejecutar.bat
echo.
pause
