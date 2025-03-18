import numpy as np
import pyautogui
import cv2
from img_handler import ImgHandler
import time
from main import circles


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


    def take_chat_references(self):
        img_handler = ImgHandler(image=self.current_screenshot)
        blue_bgr = img_handler.to_bgr_color(color=[209, 100, 0])
        hsv_color = img_handler.from_bgr_to_hsv(bgr_color=blue_bgr)
        hue = hsv_color[0][0][0]
        lower_hue = max(0, hue - 10)  # Asegura que no sea menor que 0
        upper_hue = min(179, hue + 10)  # Asegura que no sea mayor que 1

        lower_blue = np.array([lower_hue, 100, 100])  # Límite inferior
        upper_blue = np.array([upper_hue, 255, 255])

        hsv_image = img_handler.to_hsv_image()
        mask = img_handler.create_mask(image=hsv_image,
                                    lower_bound=lower_blue,
                                    upper_bound=upper_blue)
        blurred = img_handler.to_blurred_image(image=mask,
                                               ksize=(9, 9),
                                               sigmaX=2)

        circles = img_handler.detect_circles(image=blurred,
                                             dp=1,
                                             minDist=10,
                                             param1=50,
                                             param2=20,
                                             minRadius=5,
                                             maxRadius=7
                                             )

        self.last_circles_references_detected = circles

        first_circle = circles[0]
        center = (first_circle[0], first_circle[1])

        if self.chats_reference is None:
            self.chats_reference = center


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

        img_handler = ImgHandler(image=image)
        chat_id = img_handler.extract_text(image=text_roi)
        self.current_chat_id = chat_id
        return chat_id


    def scroll_chat_area(self, direction='up', scroll_move=100):
        pyautogui.moveTo(self.chats_reference[0],
                         self.chats_reference[1],
                         duration=0.3)

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