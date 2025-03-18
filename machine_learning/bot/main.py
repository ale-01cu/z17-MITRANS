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

dirname = os.path.dirname(__file__)
image_path = os.path.join(dirname, 'Captura de pantalla (19).png')
image = cv2.imread(image_path)
if image is None:
    print("No se pudo cargar la imagen. Verifica la ruta.")
    exit()

counter = 1

print("Bot Running...")

previus_screenshot = None
chats_reference = None
current_chat_id = None

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
    lower_hue = max(0, hue - 10)  # Asegura que no sea menor que 0
    upper_hue = min(179, hue + 10)  # Asegura que no sea mayor que 179

    lower_blue = np.array([lower_hue, 100, 100])  # Límite inferior
    upper_blue = np.array([upper_hue, 255, 255])  # Límite superior

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
        minDist=10,  # Distancia mínima entre centros de círculos
        param1=50,  # Sensibilidad del detector de bordes
        param2=20,  # Umbral para detectar círculos (reduce para círculos pequeños)
        minRadius=5,  # Radio mínimo del círculo (ajustado para círculos pequeños)
        maxRadius=7  # Radio máximo del círculo (ajustado para círculos pequeños)
    )

    # if previus_screenshot:
    #     previus_screenshot = cv2.resize(previus_screenshot, (image.shape[1], image.shape[0]))

    print("Circles: ", circles)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        width = image.shape[1]
        threshold_x = int(0.25 * width)  # Umbral para el 25% de la imagen desde la izquierda

        # Filtrar círculos que están en la parte izquierda pero no demasiado cerca del borde
        filtered_circles = [circle for circle in circles[0, :] if threshold_x // 2 < circle[0] < threshold_x]

        print("filtered circles: ", filtered_circles)
        for i in filtered_circles:
            x = i[0]
            y = i[1]
            center = (i[0], i[1])  # Coordenadas del centro (x, y)
            radius = i[2]          # Radio del círculo

            if chats_reference is None:
                chats_reference = center

            # Dibujar el círculo y su centro en la imagen original
            cv2.circle(image, center, 50, (0, 0, 255), 2)  # Círculo rojo con grosor de 2 píxeles
            print(f"Posición del círculo: Centro={center}, Radio={radius}")

            break
            pyautogui.click(center[0] - 100, center[1], duration=1)

            # Esperar 1 segundo antes de mover el cursor
            time.sleep(3)

            # Extract Identifier
            circle_x, circle_y = x, y
            text_roi = image[circle_y - 50:circle_y, circle_x - 250:circle_x - 80]
            identifier = img_to_text(image=text_roi)
            print(f"Identificador: {identifier}")
            cv2.imwrite(f'text_roi.png', text_roi)

            current_chat_id = identifier

            # Mover el cursor hacia la zona scroleable del chat
            pyautogui.moveTo(chats_reference[0], chats_reference[1])


            time.sleep(1)

            # Realizar un scroll hacia arriba
            pyautogui.scroll(100)  # Scroll hacia arriba (valor positivo)
            #   pyautogui.scroll(-100)  # Scroll hacia arriba (valor positivo)

            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)  # Convertir a un array NumPy
            image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            screenshot.save(f'screenshot{counter}.png')
            counter += 1

            text_extracted = img_to_text(image=image)
            print(f"Texto extraído: {text_extracted}")

            time.sleep(5)

            previus_screenshot = image

    elif previus_screenshot and mse(previus_screenshot, image) > 0:
        # Comrobar si el texto recibido es muy largo

        # Extraer texto y comprobar si el ultimo exto esxtraido de ese identificador esta en esta imagen
            # Extrar image text
            # Buscar si alguna sentencia del texto extraido de la imagen esta en el ultimo texto visto del identificador
            # del chat en el que se encuentra el bot


        # Si no lo esta hacer scroll
            # EL scroll debe ser lo suficiente como para que no repita contenido
            # Extraer Texto
            # Volver a comprobar si alguna sentencia del texto extraido de la imagen esta en el ultimo texto visto del identificador
            # del chat en el que se encuentra el bot

        # Si lo esta extraer texto
        text_extracted = img_to_text(image=image)
        print(f"Texto extraído: {text_extracted}")


    else:
        # print("Watching...")
        pass


    time.sleep(1)
  