# Messenger Scraping Bot using Computer Vision

## 1. Overview

This project is an automated bot designed to interact with the Facebook Messenger desktop application. Unlike traditional bots that rely on APIs, this bot operates through **Computer Vision** to "see" the screen, interpret the graphical user interface (GUI), and simulate human user actions.

The primary goal of the bot is to **scrape (extract) messages from conversations**. It uses image processing techniques to locate elements on the screen, controls the mouse and keyboard to navigate, and employs Optical Character Recognition (OCR) to convert the pixels of the messages into text.

## 2. Key Features

- **Visual Interface Navigation**: The bot does not depend on APIs. It navigates the Messenger application in the same way a human would: by moving the cursor, clicking, and scrolling.
- **Chat and Message Detection**: It identifies the list of chats, detects which ones have new messages, and is capable of opening them.
- **Text Extraction (Scraping)**: It locates the text bubbles of messages in a conversation, selects them, copies them to the clipboard, and processes them.
- **Handling of Scrolling and Long Content**: It can scroll vertically in a conversation to read old messages or those that do not fit on the screen. It implements logic to handle both short and very long (overflow) texts.
- **State Persistence**: It uses a SQLite database to remember the last message extracted from each conversation, thus avoiding processing the same information repeatedly.
- **Support for Multiple Resolutions**: The logic for detecting contours and coordinates is parameterized in `config.py` to adapt to different screen resolutions (e.g., `1920x1080`, `1360x768`).
- **WebSocket Communication**: It connects to a remote server via WebSockets to send the extracted data and receive commands (such as pausing or resuming its execution).
- **Window Management**: It is capable of finding the Messenger window, maximizing it, and bringing it to the foreground to ensure that the computer vision works correctly.

## 3. How It Works

The bot operates in an asynchronous main loop (`run` in `bot_module.py`) that follows these steps:

1.  **Initialization**:
    *   Loads the configuration from `config.ini` and `config.py` according to the detected screen resolution.
    *   Establishes a connection with the SQLite database to access the previous state.
    *   Initializes the WebSocket client for communication with the server.

2.  **Focus Verification**:
    *   The bot first ensures that the "Messenger" window is active and maximized using `WindowHandler`.
    *   Then, it checks if the visible interface corresponds to Messenger by comparing the current screenshot with template images (`templates/`).

3.  **Chat Detection**:
    *   Once in Messenger, it looks for available chats in the list on the left.
    *   It tries to identify if there are chats with new message notifications (currently based on the detection of reference circles).

4.  **Processing a Chat**:
    *   Upon entering a chat, the bot begins the `review_chat` process.
    *   **Chat ID Identification**: Extracts the name of the user or chat to use as a unique identifier.
    *   **Text Contour Search**: Uses `find_text_area_contours` to locate all possible message "bubbles" in the conversation area.
    *   **Overflow Handling**: Before processing, it checks if the text of the first visible message is cut off (`is_there_text_overflow`). If so, it enters a special mode (`handle_overflow_text`) to perform controlled scrolling and extract the full content of that long message.
    *   **Sequential Extraction**:
        *   It starts processing the text contours from the most recent (bottom) to the oldest (top).
        *   For each contour, it extracts the text using `get_text_by_text_location`, which simulates selection with the mouse and copying (Ctrl+C).
        *   It compares the extracted text with the last messages saved in the database for that chat. If the message has already been seen (`is_text_already_watched`), it stops the extraction for that chat.
        *   If the message is new, it sends it via WebSocket and saves it in the database as the "last seen".
    *   **Intelligent Scrolling**: If it reaches the end of the visible messages on the screen and has not found a previously seen message, it scrolls up in a calculated way to reveal older messages and repeats the extraction process.

5.  **Continuous Loop**: The bot continues to execute this cycle, looking for new messages and processing chats.

## 4. Project Structure

The code is organized into the following key files within the `bot/` directory:

-   `main_2.py`: The application's entry point. It configures and instantiates the `Bot` class and runs it.
-   `bot_module.py`: Contains the `Bot` class, which is the brain of the project and orchestrates all the high-level logic.
-   `img_handler.py`: `ImgHandler` class with all the low-level functions for image processing (masks, contours, comparison, etc.).
-   `movements_handler.py`: `MovementsHandler` class to simulate human-like mouse movements and scrolling, adding randomness and pauses.
-   `config.py`: Defines the configurations dependent on the screen resolution (coordinates, thresholds, etc.).
-   `config.ini`: Configuration file for flags and behavior parameters (e.g., `IS_MEMORY_ACTIVE`, `IS_ONLINE`).
-   `window_handler.py`: `WindowHandler` class to interact with the application window (maximize, activate, etc.).
-   `websocket_client.py`: `WebSocketClient` class that manages the connection, sending, receiving, and reconnection with the WebSocket server.
-   `db/`: Directory containing the database configuration (`db.py`), data models (`models.py` with SQLAlchemy), and queries (`bots_querys.py`, `chat_querys.py`).
-   `templates/`: Contains the template images that the bot uses to recognize the Messenger interface.

## 5. Dependencies

The project requires the following Python libraries, listed in `requirements.txt`:

-   `opencv-python`
-   `PyAutoGUI`
-   `pytesseract`
-   `SQLAlchemy`
-   `pyperclip`
-   `pytest`
-   `websockets`
-   `scikit-image`
-   `keyboard`
-   `pynput`

## 6. Installation

1.  **Install Dependencies**: Make sure you have all the libraries listed in `requirements.txt` installed in your Python environment.
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configure Tesseract**: You need to have Tesseract OCR installed on your system and the path to its executable configured in `img_handler.py`.

## 7. Usage

1.  **Adjust Configuration**:
    *   Modify `config.ini` to enable or disable features such as online connection, message memory, etc.
    *   If you use an undefined screen resolution, you will need to add a new entry in the `BOT_CONFIG` dictionary in `config.py` with the appropriate coordinates and thresholds.
2.  **Run**:
    *   Open the Messenger application and leave it visible.
    *   Execute the `main_2.py` script. The bot should take control, maximize the Messenger window, and start its work cycle.
    *   The `run.bat` script is prepared to activate a `.venv` virtual environment (if it exists) and then execute `main_2.py`.

## 8. Known Issues and Improvements

This section documents the current challenges of the project, which are the main targets for improvement:

-   **Navigation Accuracy**: The bot sometimes loses the sequence of messages when very long texts are mixed with short ones. The scrolling and re-detection logic of contours after a scroll can be unstable.
-   **Resolution Dependency**: Although there is a configuration for different resolutions, the system is not completely robust. Changes in the layout of the Messenger application, themes (light/dark), or system fonts can break the contour detection. The goal is to make it more adaptable.
-   **General Robustness**: The bot can fail if an expected contour is not found or if an action (like copying text) does not produce the expected result. More error handling and recovery mechanisms need to be added so that the bot can retry actions or re-calibrate if it gets "lost".
