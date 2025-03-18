import cv2
import numpy as np
import pyautogui
import os
import time
from img_to_text import img_to_text

dirname = os.path.dirname(__file__)
image_path = os.path.join(dirname, 'Captura de pantalla (19).png')
image = cv2.imread(image_path)
if image is None:
    print("No se pudo cargar la imagen. Verifica la ruta.")
    exit()

counter = 1

print("Bot Running...")

while True:
    # screenshot = pyautogui.screenshot()
    # frame = np.array(screenshot)  # Convertir a un array NumPy
    # image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Convertir el color #0064d1 a formato BGR
    blue_bgr = np.uint8([[[209, 100, 0]]])  # Color en formato BGR (OpenCV usa BGR)

    # Convertir el color a HSV
    hsv_color = cv2.cvtColor(blue_bgr, cv2.COLOR_BGR2HSV)

    # Extraer el valor de tono (hue)
    hue = hsv_color[0][0][0]

    # Definir rango de color en HSV con validación para el tono
    lower_hue = max(0, hue - 10)   # Asegura que no sea menor que 0
    upper_hue = min(179, hue + 10) # Asegura que no sea mayor que 179

    lower_blue = np.array([lower_hue, 100, 100])  # Límite inferior
    upper_blue = np.array([upper_hue, 255, 255]) # Límite superior

    # Convertir la imagen a HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

    # Aplicar un filtro gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)

    # Detectar círculos
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=10,       # Distancia mínima entre centros de círculos
        param1=50,        # Sensibilidad del detector de bordes
        param2=20,        # Umbral para detectar círculos (reduce para círculos pequeños)
        minRadius=5,      # Radio mínimo del círculo (ajustado para círculos pequeños)
        maxRadius=7       # Radio máximo del círculo (ajustado para círculos pequeños)
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x = i[0]
            y = i[1]
            center = (i[0], i[1])  # Coordenadas del centro (x, y)
            radius = i[2]          # Radio del círculo
            

            # Dibujar el círculo y su centro en la imagen original        
            cv2.circle(image, center, 50, (0, 0, 255), 2)  # Círculo rojo con grosor de 2 píxeles
            print(f"Posición del círculo: Centro={center}, Radio={radius}")

            pyautogui.click(center[0] - 100, center[1], duration=1)

            # Esperar 1 segundo antes de mover el cursor
            time.sleep(3)
            
            # Extract Identifier
            circle_x, circle_y = x, y
            text_roi = image[circle_y - 50:circle_y, circle_x - 250:circle_x - 80]
            identifier = img_to_text(image=text_roi)
            print(f"Identificador: {identifier}")
            cv2.imwrite(f'text_roi.png', text_roi)

            # Mover el cursor al centro de la pantalla
            screen_width, screen_height = pyautogui.size()  # Obtener dimensiones de la pantalla
            pyautogui.moveTo(screen_width // 2, screen_height // 2)  # Mover al centro de la pantalla

            # Realizar un scroll hacia arriba
            #   pyautogui.scroll(100)  # Scroll hacia arriba (valor positivo)

            time.sleep(1)

            #   pyautogui.scroll(-100)  # Scroll hacia arriba (valor positivo)
        
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)  # Convertir a un array NumPy
            image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            screenshot.save(f'screenshot{counter}.png')
            counter += 1

            text_extracted = img_to_text(image=image)
            print(f"Texto extraído: {text_extracted}")

            time.sleep(5)
    else:
        # print("No se encontraron círculos.")
        pass


    time.sleep(1)
  