@echo off
REM Script para activar el entorno virtual y ejecutar un archivo Python

REM Verificar si existe el entorno virtual
if not exist ".venv\" (
    echo No se encuentra el entorno virtual en la carpeta .venv
    pause
    exit /b
)

REM Activar el entorno virtual
call .venv\Scripts\activate

REM Ejecutar el archivo Python (cambia "tu_archivo.py" por el nombre de tu archivo)
python process_new_comments.py

REM Pausa para ver la salida (opcional)
pause