# Documentación del Bot de Messenger por Visión Artificial

## 1. Descripción General

Este proyecto es un bot automatizado diseñado para interactuar con la aplicación de escritorio de Facebook Messenger. A diferencia de los bots tradicionales que usan APIs, este opera a través de **visión artificial (Computer Vision)** para "ver" la pantalla, interpretar la interfaz gráfica y simular las acciones de un usuario humano.

El objetivo principal del bot es **scrapear (extraer) mensajes de conversaciones**. Para ello, utiliza técnicas de procesamiento de imágenes para localizar elementos en la pantalla, controla el ratón y el teclado para navegar, y emplea OCR (Reconocimiento Óptico de Caracteres) para convertir en texto los píxeles de los mensajes.

## 2. Características Principales

- **Navegación por Interfaz Visual**: El bot no depende de APIs. Navega por la aplicación de Messenger de la misma forma que un humano: moviendo el cursor, haciendo clic y scroll.
- **Detección de Chats y Mensajes**: Identifica la lista de chats, detecta cuáles tienen mensajes nuevos y es capaz de abrirlos.
- **Extracción de Texto (Scraping)**: Localiza los globos de texto de los mensajes en una conversación, los selecciona, copia al portapapeles y los procesa.
- **Manejo de Scroll y Contenido Largo**: Puede hacer scroll verticalmente en una conversación para leer mensajes antiguos o que no caben en la pantalla. Implementa una lógica para manejar tanto textos cortos como muy largos (overflow).
- **Persistencia de Estado**: Utiliza una base de datos SQLite para recordar el último mensaje extraído de cada conversación, evitando así procesar la misma información repetidamente.
- **Soporte para Múltiples Resoluciones**: La lógica de detección de contornos y coordenadas está parametrizada en `config.py` para adaptarse a diferentes resoluciones de pantalla (ej. `1920x1080`, `1360x768`).
- **Comunicación por WebSockets**: Se conecta a un servidor remoto a través de WebSockets para enviar los datos extraídos y recibir comandos (como pausar o reanudar su ejecución).
- **Manejo de Ventanas**: Es capaz de encontrar la ventana de Messenger, maximizarla y ponerla en primer plano para asegurar que la visión artificial funcione correctamente.

## 3. Flujo de Trabajo del Bot

El bot opera en un bucle principal asíncrono (`run` en `bot_module.py`) que sigue estos pasos:

1.  **Inicialización**:
    *   Carga la configuración desde `config.ini` y `config.py` según la resolución de pantalla detectada.
    *   Establece una conexión con la base de datos SQLite para acceder al estado previo.
    *   Inicia el cliente WebSocket para la comunicación con el servidor.

2.  **Verificación de Foco**:
    *   El bot primero se asegura de que la ventana de "Messenger" esté activa y maximizada usando `WindowHandler`.
    *   Luego, comprueba si la interfaz visible corresponde a Messenger, comparando la captura de pantalla actual con imágenes de plantilla (`templates/`).

3.  **Detección de Chats**:
    *   Una vez en Messenger, busca los chats disponibles en la lista de la izquierda.
    *   Intenta identificar si hay chats con notificaciones de mensajes nuevos (actualmente basado en la detección de círculos de referencia).

4.  **Procesamiento de un Chat**:
    *   Al entrar a un chat, el bot comienza el proceso de `review_chat`.
    *   **Identificación del ID del Chat**: Extrae el nombre del usuario o del chat para usarlo como identificador único.
    *   **Búsqueda de Contornos de Texto**: Utiliza `find_text_area_contours` para localizar todos los posibles "globos" de mensajes en el área de la conversación.
    *   **Manejo de Overflow**: Antes de procesar, verifica si el texto del primer mensaje visible está cortado (`is_there_text_overflow`). Si es así, entra en un modo especial (`handle_overflow_text`) para hacer scroll controlado y extraer el contenido completo de ese mensaje largo.
    *   **Extracción Secuencial**:
        *   Comienza a procesar los contornos de texto desde el más reciente (abajo) hacia los más antiguos (arriba).
        *   Para cada contorno, extrae el texto usando `get_text_by_text_location`, que simula la selección con el ratón y el copiado (Ctrl+C).
        *   Compara el texto extraído con los últimos mensajes guardados en la base de datos para ese chat. Si el mensaje ya fue visto (`is_text_already_watched`), detiene la extracción para ese chat.
        *   Si el mensaje es nuevo, lo envía por WebSocket y lo guarda en la base de datos como el "último visto".
    *   **Scroll Inteligente**: Si llega al final de los mensajes visibles en pantalla y no ha encontrado un mensaje ya visto, hace scroll hacia arriba de forma calculada para revelar mensajes más antiguos y repite el proceso de extracción.

5.  **Bucle Continuo**: El bot sigue ejecutando este ciclo, buscando nuevos mensajes y procesando chats.

## 4. Estructura del Proyecto

El código está organizado en los siguientes ficheros clave dentro del directorio `bot/`:

-   `main_2.py`: Punto de entrada de la aplicación. Configura e instancia la clase `Bot` y la ejecuta.
-   `bot_module.py`: Contiene la clase `Bot`, que es el cerebro del proyecto y orquesta toda la lógica de alto nivel.
-   `img_handler.py`: Clase `ImgHandler` con todas las funciones de bajo nivel para el procesamiento de imágenes (mascaras, contornos, comparación, etc.).
-   `movements_handler.py`: Clase `MovementsHandler` para simular movimientos humanos del ratón y scroll, añadiendo aleatoriedad y pausas.
-   `config.py`: Define las configuraciones dependientes de la resolución de pantalla (coordenadas, umbrales, etc.).
-   `config.ini`: Fichero de configuración para flags y parámetros de comportamiento (ej. `IS_MEMORY_ACTIVE`, `IS_ONLINE`).
-   `window_handler.py`: Clase `WindowHandler` para interactuar con la ventana de la aplicación (maximizar, activar, etc.).
-   `websocket_client.py`: Clase `WebSocketClient` que gestiona la conexión, envío, recepción y reconexión con el servidor WebSocket.
-   `db/`: Directorio que contiene la configuración de la base de datos (`db.py`), los modelos de datos (`models.py` con SQLAlchemy) y las consultas (`bots_querys.py`, `chat_querys.py`).
-   `templates/`: Contiene las imágenes de plantilla que el bot usa para reconocer la interfaz de Messenger.

## 5. Dependencias

El proyecto requiere las siguientes librerías de Python, listadas en `requirements.txt`:

-   `opencv-python`: Para todas las operaciones de visión artificial.
-   `PyAutoGUI`: Para el control del ratón y teclado.
-   `SQLAlchemy`: Para el ORM de la base de datos.
-   `pyperclip`: Para acceder al portapapeles del sistema.
-   `websockets`: Para la comunicación cliente-servidor.
-   `scikit-image`: Para comparaciones avanzadas de imágenes (SSIM).
-   `keyboard`: Para detectar pulsaciones de teclas (ej. 'esc' para detener).
-   `pynput`: Para bloquear eventos del ratón físico si es necesario.
-   `pytesseract`: Para el reconocimiento óptico de caracteres (OCR).

## 6. Cómo Ejecutar el Bot

1.  **Instalar Dependencias**: Asegúrate de tener todas las librerías listadas en `requirements.txt` instaladas en tu entorno de Python.
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configurar Tesseract**: Es necesario tener Tesseract OCR instalado en el sistema y la ruta a su ejecutable configurada en `img_handler.py`.
3.  **Ajustar Configuración**:
    *   Modifica `config.ini` para activar o desactivar funcionalidades como la conexión online, la memoria de mensajes, etc.
    *   Si usas una resolución de pantalla no definida, deberás añadir una nueva entrada en el diccionario `BOT_CONFIG` de `config.py` con las coordenadas y umbrales adecuados.
4.  **Ejecutar**:
    *   Abre la aplicación de Messenger y déjala visible.
    *   Ejecuta el script `main_2.py`. El bot debería tomar el control, maximizar la ventana de Messenger y comenzar su ciclo de trabajo.
    *   El script `run.bat` está preparado para activar un entorno virtual `.venv` (si existe) y luego ejecutar `main_2.py`.

## 7. Problemas Conocidos y Mejoras

Esta sección documenta los desafíos actuales del proyecto, que son los principales objetivos de mejora:

-   **Precisión en la Navegación**: El bot a veces pierde la secuencia de mensajes cuando se mezclan textos muy largos con otros cortos. La lógica de scroll y re-detección de contornos después de un desplazamiento puede ser inestable.
-   **Dependencia de la Resolución**: Aunque existe una configuración para diferentes resoluciones, el sistema no es completamente robusto. Cambios en el layout de la aplicación de Messenger, temas (claro/oscuro) o fuentes del sistema pueden romper la detección de contornos. El objetivo es hacerlo más adaptable.
-   **Robustez General**: El bot puede fallar si un contorno esperado no se encuentra o si una acción (como copiar texto) no produce el resultado esperado. Se necesita añadir más manejo de errores y mecanismos de recuperación para que el bot pueda reintentar acciones o re-calibrarse si se "pierde".
