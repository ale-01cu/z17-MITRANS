# **Documentación del Sistema de Gestión y Clasificación de Opiniones**

## 1. Resumen General

Este sistema es una aplicación web completa diseñada para gestionar la comunicación a través de Facebook Messenger. Su propósito principal es extraer mensajes de conversaciones, clasificarlos automáticamente mediante un modelo de Machine Learning y presentarlos en una interfaz de usuario intuitiva que permite su análisis y gestión.

La plataforma se compone de tres partes principales:

1.  **Backend (Django):** Un servidor robusto que maneja la lógica de negocio, la comunicación con la API de Facebook, la base de datos y la inteligencia artificial.
2.  **Frontend (React):** Una interfaz de usuario moderna y reactiva para que los operadores visualicen datos, gestionen opiniones y vean estadísticas.
3.  **Módulo de Machine Learning:** Un componente integrado en el backend para la clasificación automática de los mensajes.

## 2. Arquitectura del Sistema

### 2.1. Backend (Django)

El backend está construido con el framework Django y utiliza Django REST Framework para exponer una API RESTful.

**Tecnologías Clave:**

*   **Django:** Framework principal para el desarrollo web.
*   **Django REST Framework (DRF):** Para la creación de la API REST.
*   **Djoser:** Para la gestión de autenticación de usuarios (registro, login, etc.).
*   **Channels:** Para la comunicación en tiempo real a través de WebSockets.
*   **Celery:** Para la ejecución de tareas asíncronas en segundo plano, como la extracción de mensajes.
*   **PostgreSQL:** Como motor de base de datos.

**Estructura de Aplicaciones (`apps`):**

*   `core`: Contiene la configuración principal del proyecto (`settings.py`), el enrutamiento de URLs (`urls.py`), la configuración de Celery (`celery.py`) y el punto de entrada para WebSockets (`asgi.py`).
*   `user`: Gestiona los modelos de datos para `UserAccount`, `Entity` (para agrupar usuarios y páginas de Facebook) y `FacebookPage`.
*   `messenger`: Es el corazón de la integración con Facebook.
    *   `graphqlAPI.py`: Contiene la clase `FacebookAPIGraphql` que se comunica con la Graph API de Facebook para obtener conversaciones y mensajes.
    *   `tasks.py`: Define las tareas de Celery (`messenger_api_task`) que se ejecutan periódicamente para extraer nuevos mensajes de las páginas de Facebook configuradas.
*   `comment`, `post`, `source`, `comment_user_owner`: Definen los modelos de la base de datos para almacenar las opiniones, las publicaciones de origen, las fuentes (ej. Messenger, Facebook) y los usuarios que emiten las opiniones.
*   `classification`:
    *   Gestiona el modelo de datos `Classification` donde se almacenan las posibles categorías de un mensaje (ej. "queja", "sugerencia").
    *   Contiene el módulo de Machine Learning en `apps/classification/ml/`.
    *   Expone los endpoints de la API para clasificar comentarios (`views.py`).
*   `bot`: Implementa la lógica de WebSockets.
    *   `consumers.py`: El `ChatConsumer` maneja las conexiones en tiempo real. Recibe mensajes (tanto del frontend como de un posible bot externo), los procesa, los clasifica usando el modelo de ML y los retransmite a los clientes conectados.
*   `stats`: Proporciona los endpoints para las estadísticas que se muestran en el dashboard del frontend.

### 2.2. Frontend (React)

La interfaz de usuario es una Single Page Application (SPA) desarrollada con React.

**Tecnologías Clave:**

*   **React:** Biblioteca principal para construir la interfaz.
*   **Vite:** Herramienta de construcción y servidor de desarrollo.
*   **TypeScript:** Para un tipado estático y un código más robusto.
*   **React Router:** Para la gestión de rutas en el lado del cliente.
*   **Tailwind CSS:** Para el diseño y estilos de la aplicación.
*   **shadcn/ui (inferido):** Utiliza una colección de componentes de UI reutilizables y personalizables (en `components/ui/`) como `Card`, `Button`, `Table`, etc.
*   **Axios:** Para realizar peticiones HTTP al backend.

**Estructura de Carpetas (`app`):**

*   `api`: Contiene todas las funciones que llaman a los endpoints del backend. Cada función está encapsulada y tipada para una fácil reutilización.
*   `components`: Almacena componentes de UI reutilizables, incluyendo los componentes base de `ui` y componentes más complejos como `app-sidebar`.
*   `features`: Organiza la lógica y los componentes por funcionalidad principal de la aplicación (Dashboard, Comentarios, Usuarios, etc.).
*   `hooks`: Contiene hooks personalizados (`useAuth`, `useIsManager`, etc.) para gestionar estado y lógica compartida.
*   `layouts`: Define las plantillas de página, como `sidebar-layout.tsx` que incluye la barra de navegación lateral.
*   `routes`: Define las rutas de la aplicación, mapeando URLs a componentes de página.

### 2.3. Módulo de Machine Learning

El componente de inteligencia artificial está integrado directamente en el backend, en la ruta `backend/apps/classification/ml/`.

**Pipeline de Clasificación:**

1.  **Carga de Modelos (`model_loader.py`):** Al iniciar la aplicación Django, este script carga en memoria los modelos necesarios para evitar cargarlos en cada predicción.
2.  **Generación de Embeddings:** Un texto de entrada (un mensaje) primero se convierte en un vector numérico utilizando un modelo de `SentenceTransformer` (`paraphrase-MiniLM-L6-v2-tunned`). Este modelo ha sido afinado para entender el contexto semántico del texto en español.
3.  **Predicción:** El vector numérico generado se pasa a un modelo de clasificación `XGBoost` (`xgboost_model.json`), que predice la etiqueta final (ej. "queja", "pregunta").
4.  **Decodificación:** La etiqueta predicha, que es un número, se decodifica a su correspondiente texto (ej. de `1` a `"queja"`) usando un `label_encoder.pkl`.

Las categorías de clasificación predefinidas se encuentran en `backend/apps/classification/classifications.py`.

## 3. Flujo de Datos Principal (Extracción y Clasificación)

1.  **Tarea Programada:** Una tarea de Celery (`messenger_api_task`) se ejecuta cada cierto intervalo de tiempo.
2.  **Extracción de Datos:** La tarea itera sobre las `Entity` activas y sus `FacebookPage` asociadas. Usando el token de acceso, llama a la Graph API de Facebook a través de `graphqlAPI.py` para obtener las conversaciones y sus mensajes más recientes.
3.  **Procesamiento y Almacenamiento:**
    *   Para cada mensaje nuevo, el sistema extrae el contenido, el autor y la fecha.
    *   El texto del mensaje se envía a la función `predict_comment_label` del módulo de ML.
    *   El modelo de ML devuelve una etiqueta de clasificación (ej. "sugerencia").
    *   El sistema guarda el mensaje, su clasificación, el autor (`UserOwner`), la fuente (`Source`) y la conversación a la que pertenece en la base de datos.
4.  **Visualización en Frontend:**
    *   El usuario accede a la sección "Gestionar Opiniones".
    *   El frontend realiza una petición a la API del backend (`/api/comment/`).
    *   El backend devuelve la lista de opiniones almacenadas.
    *   La interfaz muestra los datos en una tabla, permitiendo al usuario filtrar, buscar y gestionar dichas opiniones.

## 4. Funcionalidades Clave

*   **Autenticación de Usuarios:** Sistema de inicio de sesión seguro con roles (Administrador, Gestor, Consultor).
*   **Dashboard de Estadísticas:** Visualización de métricas clave como el número total de opiniones, distribución por clasificación y una línea de tiempo de la actividad.
*   **Gestión de Opiniones:** Interfaz para ver, buscar, filtrar y editar las opiniones extraídas. Incluye paginación para manejar grandes volúmenes de datos.
*   **Clasificación Automática:** Cada opinión extraída de Messenger es clasificada automáticamente por el modelo de IA.
*   **Comunicación en Tiempo Real:** A través de WebSockets, la interfaz puede recibir notificaciones o datos en tiempo real desde el servidor.
*   **Gestión de Usuarios del Sistema:** Los administradores pueden crear y gestionar las cuentas de usuario que acceden a la plataforma.
*   **Gestión de Usuarios Emisores:** El sistema almacena y permite editar la información de los usuarios de Facebook que envían los mensajes.
*   **Importación y Exportación:** Funcionalidad para exportar opiniones a un archivo Excel e importar opiniones desde uno.

## 5. Cómo Ejecutar el Sistema

El proyecto está configurado para ser ejecutado fácilmente a través de Docker. El archivo `docker-compose.yml` en la raíz del proyecto orquesta los servicios necesarios (backend, frontend, base de datos, etc.).

Para iniciar el sistema, generalmente se ejecutaría el siguiente comando en la raíz del proyecto:

```bash
docker-compose up -d
```

Esto construirá las imágenes de los contenedores (si no existen) y levantará todos los servicios, dejando la aplicación accesible a través del navegador.
