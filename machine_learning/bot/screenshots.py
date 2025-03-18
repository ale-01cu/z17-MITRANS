import threading  # Para ejecutar la captura de pantalla en segundo plano
import time
import pyautogui
import cv2
import numpy as np

# Función para capturar screenshots cada 1 segundo
def capture_screenshots():
    screenshot_count = 0  # Contador para nombrar los archivos
    while True:
        # Capturar la pantalla
        screenshot = pyautogui.screenshot()
        print("Screenshot -> ", screenshot)

        frame = np.array(screenshot)  # Convertir a un array NumPy
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convertir de RGB a BGR (formato OpenCV)

        print("Frame cv2 -> ", screenshot)

        cv2.imshow("Screenshot", frame)
        cv2.waitKey(0)  # Esperar hasta que se cierre la ventana
        cv2.destroyAllWindows()

        
        # Guardar el screenshot con un nombre único
        # screenshot_name = f"screenshot_{screenshot_count}.png"
        # screenshot.save(screenshot_name)
        # print(f"Screenshot guardado: {screenshot_name}")
        
        # Incrementar el contador
        screenshot_count += 1
        
        # Esperar 1 segundo antes de la siguiente captura
        time.sleep(1)

# Iniciar la captura de pantalla en un hilo separado
# screenshot_thread = threading.Thread(target=capture_screenshots, daemon=True)
# screenshot_thread.start()
capture_screenshots()

# El resto del código sigue igual (detectar círculos, hacer clic, etc.)