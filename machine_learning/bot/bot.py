import numpy as np
import pyautogui
import cv2
from img_handler import ImgHandler
from img_to_text import img_to_text
import time

class Bot:
    def __init__(self):
        self.previous_screenshot = None
        self.chats_reference = None
        self.current_chat_id = None
        self.current_screenshot = None
        self.last_circles_references_detected = None


    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)  # Convertir a un array NumPy
        self.current_screenshot = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return self.current_screenshot


    def find_chat_references(self):
        img_handler = ImgHandler(image=self.current_screenshot)

        hsv_image = img_handler.to_hsv_image()
        lower_blue = np.array([100, 50, 50])
        upper_blue = np.array([130, 255, 255])

        blue_mask = img_handler.create_mask(image=hsv_image,
                                       lower_bound=lower_blue,
                                       upper_bound=upper_blue)

        # cv2.imshow('blue_mask', blue_mask)
        # cv2.waitKey(0)

        kernel = np.ones((3, 3), np.uint8)

        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

        contours = img_handler.find_contours(image=blue_mask)

        image_width = img_handler.get_shape()[1]
        image_height = img_handler.get_shape()[0]

        # Definir los límites en el eje x (5% a 25% del ancho)
        start_x = int(0.05 * image_width)  # 5% del ancho
        end_x = int(0.25 * image_width)  # 25% del ancho
        threshold_y = int(0.35 * image_height)
        contours_found = []

        for contour in contours:
            # Aproximar el contorno a un polígono
            approx = cv2.approxPolyDP(contour,
                0.04 * cv2.arcLength(contour, True), True)

            # if len(approx) >= 8:
            # Obtener el centro y el radio del círculo
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            print(center, radius)

            # Verificar si el círculo está dentro del 25% izquierdo de la imagen
            if start_x <= center[0] <= end_x and center[1] >= threshold_y:
                contours_found.append(center + (radius,))

        if len(contours_found) > 0:
            first_circle = contours_found[0]
            center = (first_circle[0], first_circle[1])

            if self.chats_reference is None:
                self.chats_reference = center

            self.last_circles_references_detected = contours_found[-1]

        return contours_found


    def click_chat(self, chat_ref: tuple[int, int], duration: int = 1):
        x = chat_ref[0]
        y = chat_ref[1]
        pyautogui.click(x - 100, y, duration=duration)
        time.sleep(3)


    def extract_chat_id(self, chat_ref: tuple[int, int]) -> str:
        x = chat_ref[0]
        y = chat_ref[1]
        circle_x, circle_y = x, y
        image = self.current_screenshot
        text_roi = image[circle_y - 50:circle_y, circle_x - 250:circle_x - 80]

        chat_id = img_to_text(image=text_roi)
        # img_handler = ImgHandler(image=image)
        # chat_id = img_handler.extract_text(image=text_roi)
        self.current_chat_id = chat_id
        return chat_id


    def extract_chat_text(self):
        text = img_to_text(image=self.current_screenshot)
        return text


    def move_to_chat(self) -> None:
        pyautogui.moveTo(self.chats_reference[0],
                         self.chats_reference[1],
                         duration=0.3
                         )


    def scroll_chat_area(self, direction='up', scroll_move=100):
        pyautogui.moveTo(self.chats_reference[0],
                         self.chats_reference[1],
                         duration=1)

        if direction == 'up':
            pyautogui.scroll(scroll_move)
        elif direction == 'down':
            pyautogui.scroll(scroll_move)


    def get_last_chat_id_text(self) -> str:
        """
        Extrae el texto del último chat id detectado.

        :return: Texto del último chat id detectado.
        """
        return ""


    def find_text(self, text: str, text_list_obj: list[str]) -> int | None:
        """
        Busca un texto en una lista de strings por coincidencia exacta.

        :param text: Texto a buscar.
        :param text_list_obj: Lista de strings en la que se buscará el texto.
        :return: Índice del texto en la lista si se encuentra, None si no se encuentra.
        """
        try:
            # Buscar el índice del texto en la lista
            index = text_list_obj.index(text)
            return index
        except ValueError:
            # Si el texto no está en la lista, retornar None
            return None


    def chat_has_more_text(self):
        # Extraer texto
        img_handler = ImgHandler(image=self.current_screenshot)
        texts = img_handler.extract_text()

        # Si el ultimo texto que vio el chat id no esta en este texto extraido entonces
        last_text = self.get_last_chat_id_text()
        index = self.find_text(text=last_text, text_list_obj=texts)

        return index


    def send_image(self):
        pass


    def run(self):
        print("Running...")
        while True:
            self.take_screenshot()
            chats = self.find_chat_references()

            for chat in chats:
                x, y = chat[0], chat[1]

                # chat_id = self.extract_chat_id(chat_ref=(x, y))

                self.click_chat(chat_ref=(x, y), duration=1)
                # self.move_to_chat()
                # self.scroll_chat_area(direction='up')
                text = self.extract_chat_text()
                # print("================= Chat ID ======================== \n \n", chat_id)
                print("================= Texto Extraido ================= \n \n", text)

                time.sleep(1)

            # if len(chats) == 0 and self.previous_screenshot is not None:
            #     img_handler = ImgHandler(image=self.current_screenshot)
            #     error = img_handler.similarity_by_mse(image=self.previous_screenshot)
            #
            #     if error > 0:
            #         text = self.extract_chat_text()
            #         print("================= Texto Extraido ================= \n \n", text)

            self.previous_screenshot = self.current_screenshot