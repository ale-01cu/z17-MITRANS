#!/bin/bash

# Iniciar worker en segundo plano
python manage.py process_tasks &

# Iniciar servidor Uvicorn
uvicorn core.asgi:application --workers 1