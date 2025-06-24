@echo off
title Levantando Aplicación
color 0A

echo #############################################
echo #                                           #
echo #    Iniciando Opicubat                     #
echo #                                           #
echo #############################################
echo.

REM Verificar si las carpetas existen
if not exist "backend\" (
    echo Error: No se encuentra la carpeta backend
    pause
    exit /b
)

if not exist "frontend\" (
    echo Error: No se encuentra la carpeta frontend
    pause
    exit /b
)

REM Función para levantar el backend Django
:start_backend
echo Iniciando Backend...
cd backend
if exist ".venv\" (
    echo Activando entorno virtual...
    call .venv\Scripts\activate
) else (
    echo Error: No se encontró el entorno virtual en backend/.venv
    pause
    exit /b
)

@REM echo Verificando dependencias...
@REM pip install -r requirements.txt > nul 2>&1
@REM if errorlevel 1 (
@REM     echo Error al instalar dependencias
@REM     pause
@REM     exit /b
@REM )

echo Iniciando servidor Django...
start cmd /k ".venv\Scripts\activate && py manage.py runserver"
cd ..
echo Servidor Django iniciado en http://127.0.0.1:8000
echo.

REM Función para levantar el frontend React
:start_frontend
echo Iniciando Frontend...
cd frontend
if not exist "node_modules\" (
    echo Instalando dependencias de Node.js...
    npm install > nul 2>&1
    if errorlevel 1 (
        echo Error al instalar dependencias de Node.js
        pause
        exit /b
    )
)

echo Iniciando servidor de desarrollo...
start cmd /k "npm run dev"
cd ..
echo Servidor React iniciado en http://localhost:5173
echo.

echo #############################################
echo #                                           #
echo #    Aplicación iniciada correctamente      #
echo #                                           #
echo #    Backend: http://localhost:8000         #
echo #    Frontend: http://localhost:5173        #
echo #                                           #
echo #############################################
echo.

pause