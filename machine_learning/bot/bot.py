import numpy as np
import pyautogui
import cv2
from img_handler import ImgHandler
from img_to_text import img_to_text
import time

class Bot:
    def __init__(self, name: str, target_name: str, target_templates_paths: list[str]) -> None:
        self.name = name
        self.target_name = target_name
        self.previous_screenshot = None
        self.chats_reference = None
        self.current_chat_id = None
        self.current_screenshot = None
        self.last_circles_references_detected = None
        self.target_templates_paths = target_templates_paths
        # self.target_template = cv2.imread(self.target_template_path)


    def is_watching_target(self, threshold: float = 0.8) -> bool:
        if self.current_screenshot is None:
            return False

        for template_path in self.target_templates_paths:
            template = cv2.imread(template_path)

            if template is None:
                continue

            h, w = template.shape[:-1]
            result = cv2.matchTemplate(self.current_screenshot,
                                       template,
                                       cv2.TM_CCOEFF_NORMED
                                       )

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                return True

        return False


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
        text_roi = image[circle_y - 50:circle_y, circle_x - 270:circle_x]

        img_hanlder = ImgHandler(image=text_roi)
        chat_id = img_hanlder.extract_text()

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



    # def extract_chat_texts(self):
    #     """
    #
    #     This function extract the texts into chat contour as little contours
    #     each text is returned as a contour.
    #
    #     :return: List of text contours
    #     """
    #     img_handler = ImgHandler(image=self.current_screenshot)
    #
    #     color_hex = '#f0f0f0'
    #     color_rgb = tuple(int(color_hex[i:i + 2], 16) for i in (1, 3, 5))  # Convierte de hex a RGB
    #     color_bgr = color_rgb[::-1]  # Convierte de RGB a BGR
    #
    #     # Establece un rango de tolerancia para capturar variaciones del color
    #     lower_bound = np.array([max(0, color_bgr[0] - 20), max(0, color_bgr[1] - 20), max(0, color_bgr[2] - 20)])
    #     upper_bound = np.array([min(255, color_bgr[0] + 13), min(255, color_bgr[1] + 13), min(255, color_bgr[2] + 13)])
    #
    #     # Paso 3: Crear una máscara para el color objetivo
    #     mask = cv2.inRange(image, lower_bound, upper_bound)
    #     result = cv2.bitwise_and(image, image,
    #                              mask=mask
    #                              )
    #
    #
    #     pass







    def send_image(self):
        pass


    def run(self):
        print("Running...")
        last_print = ""
        while True:
            self.take_screenshot()
            # is_target = self.is_watching_target()
            #
            # if not is_target:
            #     print(f"No Watching target...",
            #           end="\r" if last_print == "nowatch" else None,
            #           flush=True
            #           )
            #     last_print = "nowatch"
            #     continue
            #
            # print(f"Watching target {self.target_name}...",
            #       end="\r" if last_print == "watching" else None,
            #       flush=True
            #       )
            # last_print = "watching"

            chats = self.find_chat_references()
            for chat in chats:
                x, y = chat[0], chat[1]

                chat_id = self.extract_chat_id(chat_ref=(x, y))
                print("Chat id: ", chat_id)
                continue
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