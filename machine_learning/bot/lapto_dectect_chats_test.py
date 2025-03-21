import cv2
import numpy as np
import pyautogui
import os
import time
from img_to_text import img_to_text


def mse(img1, img2):
    # Calcular el error cuadrático medio de las dos imagenes para saber su similitud
    error = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    error /= float(img1.shape[0] * img1.shape[1])
    return error


# dirname = os.path.dirname(__file__)
# image_path = os.path.join(dirname, 'Captura de pantalla (19).png')
# image = cv2.imread(image_path)
# if image is None:
#     print("No se pudo cargar la imagen. Verifica la ruta.")
#     exit()

counter = 1

print("Bot Running...")

previus_screenshot = None
chats_reference = None
current_chat_id = None

while True:
    screenshot = pyautogui.screenshot()
    frame = np.array(screenshot)  # Convertir a un array NumPy
    image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Convertir la imagen a HSV (para facilitar la detección de colores)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Definir el rango de color azul en HSV
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([230, 255, 255])

    # Crear una máscara para detectar el color azul
    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)

    # Aplicar operaciones morfológicas para eliminar ruido
    kernel = np.ones((3, 3), np.uint8)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
    blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Obtener el ancho de la imagen
    image_width = image.shape[1]

    # Umbral para el 25% del ancho de la imagen
    threshold_x = int(0.25 * image_width)

    # Lista para almacenar las posiciones de los círculos azules
    blue_circles = []

    # Iterar sobre los contornos encontrados
    for contour in contours:
        # Aproximar el contorno a un polígono
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)

        # Si el contorno tiene aproximadamente 8 vértices, es probable que sea un círculo
        if len(approx) >= 8:
            # Obtener el centro y el radio del círculo
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            # Verificar si el círculo está dentro del 25% izquierdo de la imagen
            if center[0] <= threshold_x:
                pyautogui.click(center[0] - 100, center[1], duration=1)
                time.sleep(1)

                pyautogui.moveTo(center[0] + 200, center[1])


    time.sleep(1)
