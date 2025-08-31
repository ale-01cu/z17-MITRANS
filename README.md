# **Opinion Management and Classification System Documentation**

## 1. General Summary

This system is a comprehensive web application designed to manage communication through Facebook Messenger. Its main purpose is to extract messages from conversations, automatically classify them using a Machine Learning model, and present them in an intuitive user interface that allows for their analysis and management.

The platform consists of three main parts:

1.  **Backend (Django):** A robust server that handles business logic, communication with the Facebook API, the database, and artificial intelligence.
2.  **Frontend (React):** A modern and reactive user interface for operators to view data, manage opinions, and see statistics.
3.  **Machine Learning Module:** A component integrated into the backend for the automatic classification of messages.

## 2. System Architecture

### 2.1. Backend (Django)

The backend is built with the Django framework and uses Django REST Framework to expose a RESTful API.

**Key Technologies:**

*   **Django:** Main framework for web development.
*   **Django REST Framework (DRF):** For creating the REST API.
*   **Djoser:** For user authentication management (registration, login, etc.).
*   **Channels:** For real-time communication via WebSockets.
*   **Celery:** For executing asynchronous background tasks, such as message extraction.
*   **PostgreSQL:** As the database engine.

**Application Structure (`apps`):**

*   `core`: Contains the main project configuration (`settings.py`), URL routing (`urls.py`), Celery configuration (`celery.py`), and the entry point for WebSockets (`asgi.py`).
*   `user`: Manages the data models for `UserAccount`, `Entity` (for grouping users and Facebook pages), and `FacebookPage`.
*   `messenger`: This is the heart of the Facebook integration.
    *   `graphqlAPI.py`: Contains the `FacebookAPIGraphql` class that communicates with the Facebook Graph API to get conversations and messages.
    *   `tasks.py`: Defines the Celery tasks (`messenger_api_task`) that run periodically to extract new messages from the configured Facebook pages.
*   `comment`, `post`, `source`, `comment_user_owner`: Define the database models for storing opinions, source posts, sources (e.g., Messenger, Facebook), and the users who issue the opinions.
*   `classification`:
    *   Manages the `Classification` data model where possible message categories (e.g., "complaint", "suggestion") are stored.
    *   Contains the Machine Learning module in `apps/classification/ml/`.
    *   Exposes the API endpoints for classifying comments (`views.py`).
*   `bot`: Implements the WebSocket logic.
    *   `consumers.py`: The `ChatConsumer` handles real-time connections. It receives messages (from both the frontend and a possible external bot), processes them, classifies them using the ML model, and relays them to connected clients.
*   `stats`: Provides the endpoints for the statistics displayed on the frontend dashboard.

### 2.2. Frontend (React)

The user interface is a Single Page Application (SPA) developed with React.

**Key Technologies:**

*   **React:** Main library for building the interface.
*   **Vite:** Build tool and development server.
*   **TypeScript:** For static typing and more robust code.
*   **React Router:** For client-side route management.
*   **Tailwind CSS:** For the application's design and styling.
*   **shadcn/ui (inferred):** Uses a collection of reusable and customizable UI components (in `components/ui/`) such as `Card`, `Button`, `Table`, etc.
*   **Axios:** For making HTTP requests to the backend.

**Folder Structure (`app`):**

*   `api`: Contains all functions that call the backend endpoints. Each function is encapsulated and typed for easy reuse.
*   `components`: Stores reusable UI components, including the base components from `ui` and more complex components like `app-sidebar`.
*   `features`: Organizes logic and components by the main functionality of the application (Dashboard, Comments, Users, etc.).
*   `hooks`: Contains custom hooks (`useAuth`, `useIsManager`, etc.) to manage shared state and logic.
*   `layouts`: Defines page templates, such as `sidebar-layout.tsx` which includes the side navigation bar.
*   `routes`: Defines the application routes, mapping URLs to page components.

### 2.3. Machine Learning Module

The artificial intelligence component is integrated directly into the backend, at the path `backend/apps/classification/ml/`.

**Classification Pipeline:**

1.  **Model Loading (`model_loader.py`):** When the Django application starts, this script loads the necessary models into memory to avoid loading them for each prediction.
2.  **Embedding Generation:** An input text (a message) is first converted into a numerical vector using a `SentenceTransformer` model (`paraphrase-MiniLM-L6-v2-tunned`). This model has been fine-tuned to understand the semantic context of Spanish text.
3.  **Prediction:** The generated numerical vector is passed to an `XGBoost` classification model (`xgboost_model.json`), which predicts the final label (e.g., "complaint", "question").
4.  **Decoding:** The predicted label, which is a number, is decoded to its corresponding text (e.g., from `1` to `"complaint"`) using a `label_encoder.pkl`.

The predefined classification categories are located in `backend/apps/classification/classifications.py`.

## 3. Main Data Flow (Extraction and Classification)

1.  **Scheduled Task:** A Celery task (`messenger_api_task`) runs at a set interval.
2.  **Data Extraction:** The task iterates over active `Entity`s and their associated `FacebookPage`s. Using the access token, it calls the Facebook Graph API via `graphqlAPI.py` to get the most recent conversations and their messages.
3.  **Processing and Storage:**
    *   For each new message, the system extracts the content, author, and date.
    *   The message text is sent to the `predict_comment_label` function of the ML module.
    *   The ML model returns a classification label (e.g., "suggestion").
    *   The system saves the message, its classification, the author (`UserOwner`), the source (`Source`), and the conversation it belongs to in the database.
4.  **Frontend Visualization:**
    *   The user accesses the "Manage Opinions" section.
    *   The frontend makes a request to the backend API (`/api/comment/`).
    *   The backend returns the list of stored opinions.
    *   The interface displays the data in a table, allowing the user to filter, search, and manage these opinions.

## 4. Key Features

*   **User Authentication:** Secure login system with roles (Administrator, Manager, Consultant).
*   **Statistics Dashboard:** Visualization of key metrics such as the total number of opinions, distribution by classification, and an activity timeline.
*   **Opinion Management:** Interface to view, search, filter, and edit extracted opinions. Includes pagination to handle large volumes of data.
*   **Automatic Classification:** Every opinion extracted from Messenger is automatically classified by the AI model.
*   **Real-Time Communication:** Through WebSockets, the interface can receive notifications or real-time data from the server.
*   **System User Management:** Administrators can create and manage user accounts that access the platform.
*   **Sender User Management:** The system stores and allows editing of information for the Facebook users who send messages.
*   **Import and Export:** Functionality to export opinions to an Excel file and import opinions from one.

## 5. How to Run the System

The project is configured to be easily run via Docker. The `docker-compose.yml` file in the project root orchestrates the necessary services (backend, frontend, database, etc.).

To start the system, you would typically run the following command in the project root:

```bash
docker-compose up -d
```

This will build the container images (if they don't exist) and start all the services, making the application accessible through the browser.
