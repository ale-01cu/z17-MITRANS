import math
import numpy as np
import pyautogui
import cv2
from img_handler import ImgHandler
from img_to_text import img_to_text
import time
from db.chat_querys import ChatQuerys
from db.bots_querys import BotQuerys
import pyperclip
from typing import List, Tuple, Dict
from window_handler import WindowHandler
from utils import get_subtraction_steps
import keyboard
import asyncio
from websocket_client import WebSocketClient
from config import BOT_CONFIG
from inputs_handler import MouseBlocker

MAX_ITERATIONS = 100  # Ejemplo de límite
MAX_SCROLL_ATTEMPTS = 50  # Ejemplo de límite
pyautogui.FAILSAFE = False


class Bot:
    def __init__(self, name: str, target_name: str,
                 target_templates_paths: list[str], websocket_uri: str,
                 display_resolution: str) -> None:

        self.name = name
        self.target_name = target_name

        self.previous_screenshot = None
        self.chats_reference = None
        self.chat_area_reference = None
        self.current_chat_id = None
        self.current_screenshot = None
        self.last_circles_references_detected = None
        self.target_templates_paths = target_templates_paths
        self.scroll_reference = 0 # Cuanto se ha desplazado el scroll en el area del chat desde el fondo hacia arriba.
        self.chats_area_scroll_reference = 0 # Cuanto se ha desplazado el scroll en el area de chats (de arriba hacia abajo).
        # self.target_template = cv2.imread(self.target_template_path)
        self.chat_querys = ChatQuerys()
        self.bot_querys = BotQuerys()

        current_bot = self.bot_querys.get_bot_by_name(self.name)

        if not current_bot:
            self.bot_querys.create_bot(name=self.name,
                                       is_in_message_requests_view=False)

        # Initialize WebSocket client
        self.websocket = WebSocketClient(
            uri=websocket_uri,
        )
        self.websocket_uri = websocket_uri
        self.window_handler = WindowHandler(title=target_name, is_active=True)
        self.first_contour_reference: Tuple[int, int, int, int] | None = None

        # self.is_in_message_requests_view = current_bot.name if current_bot else (
        #     self.bot_querys.get_bot_by_name(name=self.name).is_in_message_requests_view)

        self.is_online = False

        # Esta propiedad sirve para activar o desactivar a funcion
        # de guardar el ultimo texto visto en la base de datos y de
        # solo tomar hasta ese ultimo texto. Si esta en False no lo hará
        self.is_memory_active = False
        self.is_only_check = False # Solo para en base al ultimo comentario que ha visto pero no guarda


        self.was_handled_overflow = False
        self.messages_amount_limit = 50

        # Variable para guardar los ultimos textos hasta 5
        # que se vean de un chat, se guardan aqui primero
        # para luego guardarlos en la base de datos.
        # Esto pasa asi porque no se puede guardar los textos cuando se extraen
        # deben de guardarse luego de revisar los textos no vistos.
        self.last_five_texts_memory_db = []
        self.last_five_texts_memory_db_v2: Dict[str, None | str] = {
            'last_text': None,
            'msg2': None,
            'msg3': None,
            'msg4': None,
            'msg5': None
        }

        self.is_show_contours_active = False

        self.amount_of_time_chats_area_down_scrolled = 0

        self.is_paused = False

        self.display_resolution = display_resolution

        # self.mouse_blocker = MouseBlocker(blocked=True)


    def add_last_five_texts_watched(self, last_text: str | None,
                                    msg_2: str | None = None, msg_3: str | None = None,
                                    msg_4: str | None = None, msg_5: str | None = None,
                                    is_fill: bool = True) -> None | bool:

        if is_fill:
            if not last_text:
                return None

            self.last_five_texts_memory_db = []
            self.last_five_texts_memory_db.append(last_text)
            if msg_2:
                self.last_five_texts_memory_db.append(msg_2)
            if msg_3:
                self.last_five_texts_memory_db.append(msg_3)
            if msg_4:
                self.last_five_texts_memory_db.append(msg_4)
            if msg_5:
                self.last_five_texts_memory_db.append(msg_5)

        else:
            if last_text:
                self.last_five_texts_memory_db[0] = last_text
            if msg_2:
                self.last_five_texts_memory_db[1] = msg_2
            if msg_3:
                self.last_five_texts_memory_db[2] = msg_3
            if msg_4:
                self.last_five_texts_memory_db[3] = msg_4
            if msg_5:
                self.last_five_texts_memory_db[4] = msg_5


        return True

    def add_last_five_texts_watched_v2(self, text:str) -> None | bool:
        if not text:
            return None

        if len(self.last_five_texts_memory_db) >= 5:
            return None

        self.last_five_texts_memory_db.append(text)

        return True

    def add_last_five_texts_watched_v3(self, last_text: str | None,
                                    msg_2: str | None = None, msg_3: str | None = None,
                                    msg_4: str | None = None, msg_5: str | None = None,
                                   add_to_first_empty: bool = False
                                    ) -> None | bool:

        if add_to_first_empty and last_text is not None:
            for key in self.last_five_texts_memory_db_v2:
                if self.last_five_texts_memory_db_v2[key] is None:
                    self.last_five_texts_memory_db_v2[key] = last_text
                    break  # Solo añade en el primer hueco encontrado
            return True

        if last_text:
            self.last_five_texts_memory_db_v2['last_text'] = last_text

        if msg_2:
            self.last_five_texts_memory_db_v2['msg2'] = msg_2

        if msg_3:
            self.last_five_texts_memory_db_v2['msg3'] = msg_3

        if msg_4:
            self.last_five_texts_memory_db_v2['msg4'] = msg_4

        if msg_5:
            self.last_five_texts_memory_db_v2['msg5'] = msg_5



    def clear_texts_not_watched(self) -> None:
        self.last_five_texts_memory_db.clear()

    def clear_texts_not_watched_v2(self) -> None:
        self.last_five_texts_memory_db_v2 = {
            'last_text': None,
            'msg2': None,
            'msg3': None,
            'msg4': None,
            'msg5': None
        }


    def get_last_five_texts_memory_db(self):
        return self.last_five_texts_memory_db[: 5]


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


    def is_watching_target_v2(self, threshold: float = 0.8):
        if self.current_screenshot is None:
            return False

        template = cv2.imread(self.target_templates_paths[0])

        if template is None:
            return False

        chats_contour = self.take_chats_container_contour()
        chat_area_contour = self.find_chat_area_contour()

        ignored_contours = []

        if chats_contour is not None:
            ignored_contours.append(chats_contour)

        if chat_area_contour is not None:
            ignored_contours.append(chat_area_contour)


        img_handler = ImgHandler(image=self.current_screenshot)
        _, _, score = img_handler.compare_messenger_images_with_contours(img_data2=template,
                                                           ignored_contours=ignored_contours)

        if score > threshold:
            return True

        return False



    def take_screenshot(self):
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)  # Convertir a un array NumPy
        self.current_screenshot = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # self.current_screenshot = cv2.cvtColor(image_test, cv2.COLOR_RGB2BGR)
        return self.current_screenshot


    def take_chats_container_contour(self):
        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()

        chats_contour = None

        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)

            if chats_contour is None:
                chats_contour = contour

            x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

            if chats_contour is not None and x == 0 and y_chats > y and h_chats < h:
                chats_contour = contour

        self.chats_reference = chats_contour
        return self.chats_reference


    def find_chat_area_contour(self, image = None):
        img_handler = ImgHandler(image=self.current_screenshot if image is None else image)
        contours = img_handler.find_contours_by_large_contours_mask()
        chats_contour = self.take_chats_container_contour()
        possible_chat_contours = []
        margin = 20
        chat_contour = None

        # Find possible chat contour nearby | Tested
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

            if x < 50 or h < 20:
                continue

            if abs(x - (x_chats + w_chats)) < margin:
                possible_chat_contours.append(contour)

        # cv2.drawContours(self.current_screenshot, possible_chat_contours, -1, (0, 255, 0), 3)
        # cv2.imshow('chats mark', self.current_screenshot)
        # cv2.waitKey(0)

        # Find chat contour | Tested
        for contour in possible_chat_contours:
            x, y, w, h = cv2.boundingRect(contour)

            if chat_contour is None:
                chat_contour = contour

            if chat_contour is not None:
                x_chat, y_chat, w_chat, h_chat = cv2.boundingRect(chat_contour)
                if w_chat * h_chat < w * h:
                    chat_contour = contour

        x_chat, y_chat, w_chat, h_chat = cv2.boundingRect(chat_contour)
        self.chat_area_reference = (x_chat, y_chat, w_chat, h_chat)
        return chat_contour


    def find_button_to_bottom_contour(self) -> List | None:
        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()
        chat_contour = self.find_chat_area_contour()
        button_contour_found = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filtro básico de tamaño (elimina ruido)
            if w > 20 and h > 20:
                # Obtener coordenadas del chat_contour (área de referencia)
                x_ref, y_ref, w_ref, h_ref = cv2.boundingRect(chat_contour)

                # --- Condiciones de posición ---
                # 1. Zona central en X (30%-70%)
                start_x = x_ref + int(w_ref * 0.3)
                end_x = x_ref + int(w_ref * 0.7)
                in_center_x = (x >= start_x) and (x + w <= end_x)

                # 2. Zona inferior en Y (últimos 30% hacia abajo)
                start_y = y_ref + int(h_ref * 0.6)  # 70% desde arriba = 30% inferior
                in_bottom_y = (y >= start_y) and (y + h <= y_ref + h_ref)  # No se sale por abajo

                # Verificar ambas condiciones
                if in_center_x and in_bottom_y:
                    button_contour_found.append(contour)

        if len(button_contour_found) == 0:
            return None


        button_contour = button_contour_found[0]

        for contour in button_contour_found:
            x, y, w, h = cv2.boundingRect(contour)
            x_aux, y_aux, w_aux, h_aux = cv2.boundingRect(button_contour)

            if w > w_aux and h > h_aux:
                button_contour = contour


        # button_contour_found = max(button_contour_found, key=cv2.contourArea)
        return button_contour


    def find_current_chat_id(self):
        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()
        chat_id_contour = contours[0] if contours and len(contours) > 0 else None

        if chat_id_contour is None: return None

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            x_target, y_target, w_target, h_target = cv2.boundingRect(chat_id_contour)

            if w > w_target and y < y_target:
                chat_id_contour = contour

        x, y, w, h = cv2.boundingRect(chat_id_contour)

        image = self.current_screenshot

        # Calculamos las coordenadas de la región de interés (ROI)
        # Comienza donde termina el contorno (y + h) y tiene el mismo ancho (w) y altura (h)
        roi_y_start = y + h + 10
        roi_y_end = roi_y_start + h + 10  # Misma altura que el contorno
        height, width = image.shape[:2]

        config = BOT_CONFIG[self.display_resolution]['FIND_CURRENT_CHAT_ID']
        roi_x_start_porcent = config['roi_x_start_porcent']

        # Calcular punto de inicio X al 30% del ancho de la imagen
        roi_x_start = int(width * roi_x_start_porcent)  # 30% del ancho total
        roi_x_end = x + int(w * 0.6)

        # Aseguramos que no nos salgamos de los límites de la imagen
        height, width = image.shape[:2]
        roi_y_end = min(roi_y_end, height)
        roi_x_end = min(roi_x_end, width)

        # Extraemos la región de interés
        roi = image[roi_y_start:roi_y_end, roi_x_start:roi_x_end]


        img_hanlder = ImgHandler(image=roi)
        texts = img_hanlder.extract_text()
        chat_id = None

        if texts and len(texts) > 0:
            sentences = [line.strip() for line in texts.split('\n') if line.strip()]
            chat_id = sentences[0]
        else:
            raise ValueError("No se pudo extraer el chat id.")

        if chat_id is None:
            return None

        print("chat id ", chat_id)

        # self.show_contours(image=roi, contours=[],
        #                    title=f'chat id')
        self.current_chat_id = chat_id
        # self.show_contours(image=roi, contours=[],
        #                    title=f'chat id extracted {chat_id}')

        return chat_id


    async def is_photo_contour(self, contour_target):
        # Obtener todos los contornos dentro del chat area
        # Convertir a escala de grises
        gray = cv2.cvtColor(self.current_screenshot, cv2.COLOR_BGR2GRAY)

        # Aplicar desenfoque más agresivo para reducir ruido
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # Binarización adaptativa con parámetros ajustados
        thresh = cv2.adaptiveThreshold(blurred, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 21, 5)

        # Eliminar ruido con operaciones morfológicas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        # Encontrar contornos
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        possible_text_contours = []
        chat_contour = self.find_chat_area_contour()

        config = BOT_CONFIG[self.display_resolution]['FIND_TEXT_AREA_CONTOURS']
        chat_limit_x_porcent = config['chat_limit_x_porcent_in_message_requests_view'] \
            if self.is_in_principal_view() else config['chat_limit_x_porcent']
        min_height = config['min_height']
        chat_start_x_porcent = config['chat_start_x_porcent']

        x_chat, y_chat, w_chat, h_chat = cv2.boundingRect(chat_contour)
        chat_limit_x = x_chat + int(
            (x_chat + w_chat) * chat_limit_x_porcent)  # Punto medio horizontal del chat subir esto

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            perimeter = cv2.arcLength(contour, True)

            # Filtro de tamaño (ajusta según necesidad)
            min_w = 40
            min_h = 0

            # Verifica si tiene el tamaño adecuado
            if (min_w < w < w_chat * 0.70) and (min_h < h < h_chat - 10):
                # Verifica si no pasa el limite en el eje y inferior
                use_first_contour_reference = True
                is_contour_valid = y + h < self.first_contour_reference[1] + self.first_contour_reference[-1] \
                    if self.first_contour_reference is not None and use_first_contour_reference \
                    else True

                # is_contour_valid = True

                is_within_chat_width_percent = x + w <= chat_limit_x

                # is_within_chat_width_percent = True

                # Verificar si comienza donde mismo comienza el primer contorno de referencia
                x_reference = self.first_contour_reference[0] if self.first_contour_reference is not None else 0
                is_x_valid = (x == x_reference or x_reference - 5 < x < x_reference + 5) \
                    if x_reference != 0 else True

                # Verifica si está DENTRO del chat_contour
                if (((x_chat < x < (x_chat + w_chat) * chat_start_x_porcent) and (x + w < x_chat + w_chat))
                        and ((y > y_chat) and (y + h < y_chat + h_chat))
                        and is_contour_valid
                        and is_within_chat_width_percent
                        and is_x_valid
                ):
                    possible_text_contours.append(contour)


        def is_contour_unique(new_cnt, existing_cnts, threshold=5):
            """
            Devuelve True si el contorno new_cnt no está cerca de ninguno en existing_cnts.
            Se compara la distancia entre bounding boxes.
            """
            x1, y1, w1, h1 = cv2.boundingRect(new_cnt)
            for cnt in existing_cnts:
                x2, y2, w2, h2 = cv2.boundingRect(cnt)
                if abs(x1 - x2) < threshold and abs(y1 - y2) < threshold and \
                        abs(w1 - w2) < threshold and abs(h1 - h2) < threshold:
                    return False
            return True


        text_contours = self.find_text_area_contours()

        filtered_contours = [cnt for cnt in possible_text_contours if is_contour_unique(cnt, text_contours)]

        self.show_contours(contours=[contour_target], title='contour target')
        self.show_contours(contours=filtered_contours, title='filtered_contours')

        for contour in filtered_contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_target, y_target, w_target, h_target = cv2.boundingRect(contour_target)

            # Check if target contour is inside contour
            if x < x_target < x + w and y_target > y and y_target + h_target < y + h:
                return True

        return False


    def find_text_area_contours(self, image = None,
                                use_first_contour_reference = True,
                                take_all_texts=False, is_other_way=False,
                                ):
        # img_handler = None
        #
        # if self.is_in_message_requests_view:
        #     chat_area_cropped = self.get_chat_area_cropped()
        #     img_handler = ImgHandler(image=chat_area_cropped)
        #
        # else:
        #     img_handler = ImgHandler(image=self.current_screenshot if image is None else image)

        img_handler = ImgHandler(image=self.current_screenshot if image is None else image)
        contours = None

        if is_other_way:
            contours = img_handler.find_texts_area_contours()
            # self.show_contours(contours=contours, title="find_texts_area_contours")

        else:
            contours = img_handler.find_contours_by_large_contours_mask()
            # self.show_contours(contours=contours, title="find_contours_by_large_contours_mask")

        # self.show_contours(contours=contours, title="find_text_area_contours")

        possible_text_contours = []
        chat_contour = self.find_chat_area_contour()

        # self.show_contours(image=chat_area_cropped, contours=contours,
        #                    title="posible texto contour-find_text_area_contours")

        # self.show_contours(contours=contours,
        #                    title=f"contours-find_text_area_contours")

        # self.show_contours(contours=chat_contour,
        #                    title="chat_contour-find_text_area_contours")

        config = BOT_CONFIG[self.display_resolution]['FIND_TEXT_AREA_CONTOURS']
        chat_limit_x_porcent = config['chat_limit_x_porcent_in_message_requests_view'] \
            if self.is_in_principal_view() else config['chat_limit_x_porcent']
        min_height = config['min_height']
        chat_start_x_porcent = config['chat_start_x_porcent']

        x_chat, y_chat, w_chat, h_chat = cv2.boundingRect(chat_contour)
        chat_limit_x = x_chat + int((x_chat + w_chat) * chat_limit_x_porcent)   # Punto medio horizontal del chat subir esto

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            perimeter = cv2.arcLength(contour, True)


            # Filtro de tamaño (ajusta según necesidad)
            min_w = 40 if take_all_texts else 100
            min_h = 0 if take_all_texts else min_height # bajar esto
            # max_chat_width_porcent = 0.60 if self.is_in_message_requests_view else 0.70

            # Verifica si tiene el tamaño adecuado
            if (min_w < w < w_chat * 0.70) and (min_h < h < h_chat - 10):
                # Verifica si no pasa el limite en el eje y inferior
                is_contour_valid = y + h < self.first_contour_reference[1] + self.first_contour_reference[-1] \
                    if self.first_contour_reference is not None and use_first_contour_reference \
                    else True

                # is_contour_valid = True

                is_within_chat_width_percent = x + w <= chat_limit_x

                # is_within_chat_width_percent = True

                # Verificar si comienza donde mismo comienza el primer contorno de referencia
                x_reference = self.first_contour_reference[0] if self.first_contour_reference is not None else 0
                is_x_valid = (x == x_reference or x_reference - 5 < x < x_reference + 5) \
                    if x_reference != 0 else True

                # Verifica si está DENTRO del chat_contour
                if (((x_chat < x < (x_chat + w_chat) * chat_start_x_porcent) and (x + w < x_chat + w_chat))
                    and ((y > y_chat) and (y + h < y_chat + h_chat))
                    and is_contour_valid
                    and is_within_chat_width_percent
                    and is_x_valid
                    ):

                    possible_text_contours.append(contour)

        # cv2.drawContours(self.current_screenshot, possible_text_contours, -1, (0, 255, 0), 3)
        # cv2.imshow('chats contour', self.current_screenshot)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        if not is_other_way and len(possible_text_contours) == 0:
            return self.find_text_area_contours(is_other_way=True,
                                                image=image,
                                                use_first_contour_reference=use_first_contour_reference,
                                                take_all_texts=take_all_texts)

        return possible_text_contours


    # TODO: Agregar que encuentre los puentos dentro del contorno donde van los chats
    # para achicar el cerco y disminuir el error
    def find_chat_references(self):
        self.take_screenshot()
        img_handler = ImgHandler(image=self.current_screenshot)
        edged = img_handler.get_edged()
        contours = img_handler.find_contours(image=edged)
        chats_contour = self.take_chats_container_contour()
        # self.show_contours(contours=[chats_contour], title='chats contour')
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

        # self.show_contours(contours=contours, title='Contours')

        contours_found = []

        for i, contour in enumerate(contours):
            # Calcular el área y el perímetro del contorno
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            x, y, w, h = cv2.boundingRect(contour)

            # Evitar división por cero
            if perimeter == 0:
                continue

            # Calcular la circularidad
            circularity = (4 * np.pi * area) / (perimeter ** 2)


            is_into_chats_contour = (
                x > (x_chats + 0.70 * w_chats) and  # Comienza después del 70% del ancho (últimos 30%)
                x < (x_chats + w_chats) and  # Termina al final del ancho
                y > (y_chats + 0.10 * h_chats) and  # Comienza después del 10% del alto
                y < (y_chats + h_chats)  # Termina al final del alto
            )

            config = BOT_CONFIG[self.display_resolution]['FIND_CHATS_REFERENCE']
            min_width = config['min_width']
            max_width = config['max_width']
            min_height = config['min_height']
            max_height = config['max_height']

            is_in_size_range = (
                (min_width < w < max_width) and (min_height < h < max_height)
            )

            # Filtrar contornos basados en la circularidad (ajusta el umbral según sea necesario)
            if 0.7 < circularity <= 1.0 and is_into_chats_contour and is_in_size_range:  # Umbral de circularidad
                contours_found.append(contour)

        # self.show_contours(contours=contours_found, title='chats contours')

        # for contour in contours:
        #     # Aproximar el contorno a un polígono
        #     approx = cv2.approxPolyDP(contour,
        #         0.04 * cv2.arcLength(contour, True), True)
        #
        #     # if len(approx) >= 8:
        #     # Obtener el centro y el radio del círculo
        #     (x, y), radius = cv2.minEnclosingCircle(contour)
        #     center = (int(x), int(y))
        #     radius = int(radius)
        #
        #     # Verificar si el círculo está dentro del 25% izquierdo de la imagen
        #     # Verificar si el circulo esta dentro del contorno donde estan los chats
        #     # if start_x <= center[0] <= end_x and center[1] >= threshold_y:
        #     self.take_chats_container_contour()
        #     # if x > self.chats_reference[0] and x < self.chats_reference[0] + self.chats_reference[2] \
        #     #     and y < self.chats_reference[1] and y < self.chats_reference[1] + self.chats_reference[3]:
        #     print("\n chats references: ", self.chats_reference)
        #     contours_found.append(center + (radius,))

        if len(contours_found) > 0:
            first_circle = contours_found[0]
            center = (first_circle[0], first_circle[1])

            # if self.chats_reference is None:
            #     self.chats_reference = center

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

        config = BOT_CONFIG[self.display_resolution]['EXTRACT_CHAT_ID']
        y_sub = config["y_sub"]
        y_plus = config["y_plus"]
        x_sub = config["x_sub"]

        text_roi = image[
                   circle_y - y_sub:circle_y + y_plus,
                   circle_x - x_sub:circle_x]

        # self.show_contours(image=text_roi,
        #                    contours=[], title="text_roi")

        img_hanlder = ImgHandler(image=text_roi)
        chat_id = img_hanlder.extract_text()
        if chat_id: chat_id = chat_id.strip()
        else: raise ValueError("No se pudo extraer el chat id.")

        self.current_chat_id = chat_id
        return chat_id


    def extract_chat_text(self):
        text = img_to_text(image=self.current_screenshot)
        return text


    def move_to_chat(self) -> None:
        # assert self.chat_area_reference is None, \
        #     "move_to_chat error: Chat area reference is None."
        chat_area = self.find_chat_area_contour()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chat_area)

        # pyautogui.moveTo(x=x_chats + w_chats / 2,
        #                  y=y_chats + h_chats / 2,
        #                  duration=0.3
        #                  )
        pyautogui.moveTo(x=x_chats + (w_chats - 15),
                         y=y_chats + (h_chats / 2),
                         duration=1
                         )


    def scroll_chat_area(self, direction='up', scroll_move=100, move_to_chat=True):
        if move_to_chat:
            self.move_to_chat()
            # pyautogui.leftClick()


        if self.scroll_reference is None:
            self.scroll_reference = scroll_move
        elif direction == 'up' and self.scroll_reference is not None:
            self.scroll_reference += scroll_move
        elif direction == 'down' and self.scroll_reference is not None:
            self.scroll_reference -= scroll_move

        if direction == 'up':
            pyautogui.scroll(abs(scroll_move))
        elif direction == 'down':
            pyautogui.scroll(-abs(scroll_move))


    def scroll_chats_area(self, direction='up', scroll_move=100, move_to_chats_area=True):
        chats_contour = self.take_chats_container_contour()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

        if move_to_chats_area:
            pyautogui.moveTo(x=x_chats + w_chats / 2,
                             y=y_chats + h_chats / 2,
                             duration=1
                             )

        if self.chats_area_scroll_reference is None:
            self.chats_area_scroll_reference = scroll_move
        elif direction == 'up' and self.scroll_reference is not None:
            self.chats_area_scroll_reference += scroll_move
        elif direction == 'down' and self.chats_area_scroll_reference is not None:
            self.chats_area_scroll_reference -= scroll_move

        if direction == 'up':
            pyautogui.scroll(abs(scroll_move))
        elif direction == 'down':
            pyautogui.scroll(-abs(scroll_move))


    def get_last_chat_id_image(self) -> ImgHandler:
        """
        Extrae el texto del último chat id detectado.

        :return: Texto del último chat id detectado.
        """
        chat_data = self.chat_querys.get_chat_by_id_scraped(
            id_scraped=self.current_chat_id)
        img_handler = ImgHandler(image=chat_data.last_text_url)
        return img_handler


    def get_last_chat_id_text_and_index(self) -> Tuple[str, int] | None:
        """
        Extrae el texto del último chat id detectado.

        :return: Texto del último chat id detectado.
        """
        chat_data = self.chat_querys.get_chat_by_id_scraped(
            id_scraped=self.current_chat_id)

        if not chat_data: return None
        return chat_data.last_text, chat_data.last_text_index


    def get_last_five_texts_by_current_chat_id(self
                                               ) -> Tuple[str | None, str | None, str | None, str | None, str | None] | None:
        """
        Extrae el texto del último chat id detectado.

        :return: Texto del último chat id detectado.
        """
        chat_data = self.chat_querys.get_chat_by_id_scraped(
            id_scraped=self.current_chat_id)

        if not chat_data: return None
        return chat_data.last_text, chat_data.msg2, chat_data.msg3, chat_data.msg4, chat_data.msg5


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
        last_text, _ = self.get_last_chat_id_text_and_index()
        index = self.find_text(text=last_text, text_list_obj=texts)

        return index


    def is_there_text_overflow(self, chat_contour):
        img_handler = ImgHandler(image=self.current_screenshot)
        has_downward_deviation = img_handler.is_top_edge_irregular(contour=chat_contour,
                                                        analyze_percent=25)

        # has_discontinuity = img_handler.has_irregular_horizontal_edge(contour=chat_contour)
        return has_downward_deviation


    def is_contour_already_watched(self, contour) -> bool:
        img_handler = self.get_last_chat_id_image()
        contour_image = img_handler.contour_to_image(contour=contour)
        similarity_error = img_handler.similarity_by_mse(image=contour_image)

        if similarity_error < 0.1:
            return True
        return False


    def is_text_already_watched(self, text: str, index: int) -> bool:
        """
        Comprueba si el texto ya ha sido visto por el chat id actual.

        :param text: Texto a comprobar.
        :param index: Índice del texto actual.
        :return: True si el texto ya ha sido visto, False en caso contrario.
        """
        # Si la memoria no está activa o solo se está comprobando, no hay nada que comparar
        if not self.is_memory_active and not self.is_only_check:
            return False

        # Obtener el último texto y su índice desde la base de datos
        data = self.get_last_five_texts_by_current_chat_id()

        # Si alguno de los textos es None o vacío, no hay coincidencia
        if not data or not text:
            return False

        # Normalizar los textos antes de comparar
        def normalize_text(input_text: str | None) -> str:
            if not input_text:
                return ""
            # Eliminar espacios adicionales, saltos de línea y tabulaciones
            normalized = input_text.strip()
            # Convertir a minúsculas para hacer la comparación insensible a mayúsculas/minúsculas
            normalized = normalized.lower()
            # Asegurarse de que no haya caracteres invisibles adicionales
            normalized = " ".join(normalized.split())
            return normalized

        # Normalizar ambos textos
        data_normalized = [normalize_text(text) for text in data]
        text_normalized = normalize_text(text)

        # print("text_normalized ", text_normalized)
        # print('data_normalized ', data_normalized)

        # Comparar los textos normalizados
        return text_normalized in data_normalized


    def show_contours(self, contours, title: str = "title", image = None):
        if not self.is_show_contours_active: return
        image_copy = self.current_screenshot.copy() if image is None else image.copy()
        cv2.drawContours(image_copy if image is None else image,
                         contours, -1, (0, 255, 0), 3)
        cv2.imshow(title, image_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    async def move_to_contour_gradually(self, target_x,
                                        target_y, check_steps=5,
                                        step_delay=0, is_first_iter=False):
        """Mueve el cursor gradualmente hacia el contorno objetivo, verificando los contornos en cada paso"""
        current_x, current_y = pyautogui.position()
        total_steps = check_steps
        last_text_contour_checked = None

        for step in range(1, total_steps + 1):
            # Calcular posición intermedia
            intermediate_x = current_x + (target_x - current_x) * (step / total_steps)
            intermediate_y = current_y + (target_y - current_y) * (step / total_steps)

            # Mover a posición intermedia
            pyautogui.moveTo(intermediate_x, intermediate_y, duration=0.1)

            # Volver a capturar pantalla y contornos
            self.take_screenshot()
            possible_text_contours = self.find_text_area_contours(use_first_contour_reference=not is_first_iter,
                                                                  )

            # self.show_contours(contours=possible_text_contours,
            #                    title='todos los contornos move_to_contour_gradually')

            # Si hay contornos, actualizar target con el primero
            if possible_text_contours and len(possible_text_contours) > 0:
                # self.show_contours(contours=possible_text_contours[0], title='el utltimo contorno')
                x, y, w, h = cv2.boundingRect(possible_text_contours[0])
                target_x = x + 15
                target_y = y + 15

                if step == total_steps:
                    last_text_contour_checked = possible_text_contours[0]

            await asyncio.sleep(step_delay)

        return last_text_contour_checked


    def is_link(self, current_contour, next_contour):
        if next_contour is None:
            return False
        # Obtener los rectángulos delimitadores de ambos contornos
        x1, y1, w1, h1 = cv2.boundingRect(current_contour)
        x2, y2, w2, h2 = cv2.boundingRect(next_contour)

        # Borde superior del current_contour: y1
        # Borde inferior del next_contour: y2 + h2
        distance = y1 - (y2 + h2)

        print(f"distance {distance}")

        # self.show_contours(contours=[current_contour, next_contour],
        #                    title=f'distance {distance}')

        # Si la distancia es 0 o menor (pueden estar tocándose o solapados), devolvemos True
        return distance <= 0


    async def get_texts_did_not_watched_list(self, possible_text_contours,
                                             is_first_iter=False, texts=[], was_handled_overflow=False):
        texts_did_not_watched = []
        has_more = True
        skip_next_contour = False
        img_handler = ImgHandler(image=self.current_screenshot)
        last_text = None
        msg2 = None
        msg3 = None
        msg4 = None
        msg5 = None

        if possible_text_contours is None or len(possible_text_contours) < 1:
            return has_more, texts_did_not_watched


        self.move_to_chat()

        # self.show_contours(contours=possible_text_contours,
        #     title=f"posible contornos de texts is_first_iter {is_first_iter}")

        first_text = possible_text_contours[0]
        is_photo = await self.is_photo_contour(contour_target=first_text)

        # self.show_contours(contours=[first_text], title=f'is photo: {is_photo}')

        if is_first_iter and not is_photo:
            x, y, w, h = cv2.boundingRect(first_text)

            is_top_edge_irregular = img_handler.is_top_edge_irregular(contour=first_text,
                                                                        threshold=1,
                                                                        edge_margin_left=5,
                                                                        edge_margin_right=5,
                                                                        analyze_percent=100)

            is_bottom_edge_irregular = img_handler.is_bottom_edge_irregular(contour=first_text,
                                                                            threshold=1,
                                                                            edge_margin_left=5,
                                                                            edge_margin_right=5,
                                                                            analyze_percent=100)


            # self.show_contours(contours=[first_text], title=f"first text contour "
            #                                                 f"is_top_edge_irregular {is_top_edge_irregular}"
            #                                                 f"is_bottom_edge_irregular {is_bottom_edge_irregular}")

            if False:
                # self.show_contours(contours=[], title=f"testing  ")
                if is_top_edge_irregular: skip_next_contour = True

            else:
                skip_next_contour = False

                config = BOT_CONFIG[self.display_resolution]['GET_TEXTS_DID_NOT_WATCHED']
                x_start_offset = config['x_start_offset']
                y_start_offset = config['y_start_offset']

                # self.show_contours(contours=[first_text], title='el primer contorno')
                if is_first_iter and not was_handled_overflow:
                    first_text_gradually = await self.move_to_contour_gradually(x+x_start_offset,
                                                                      y+y_start_offset,
                                                                      is_first_iter=is_first_iter)
                    if first_text_gradually is not None:
                        first_text = first_text_gradually

                x, y, w, h = cv2.boundingRect(first_text)
                # self.show_contours(contours=[first_text], title='el primer contorno')

                text = self.get_text_by_text_location(
                    x_start=x - 5,
                    y_start=y - y_start_offset,
                    x_end=x + w,
                    y_end=(y + h) - 15,
                    scroll_pos_start=self.scroll_reference,
                    scroll_pos_end=self.scroll_reference,
                    desactivate_scroll=True
                )

                if self.is_online: await self.websocket.send_websocket_message(
                    message_type="bot_message", message=text,
                    name=self.name, current_chat_id=self.current_chat_id)


                if self.first_contour_reference is None:
                    # self.show_contours(contours=[first_text], title='tirst contour reference')
                    self.first_contour_reference = (x, y, w, h)

                is_watched = self.is_text_already_watched(text=text, index=len(texts))

                if not is_watched:
                    start_location = (x, y, self.scroll_reference)
                    end_location = (x + w, y + h, self.scroll_reference)
                    texts_did_not_watched.append([start_location, end_location])

                    if text:
                        last_text = text
                        # self.chat_querys.update_chat_by_chat_id_scraped(
                        #     id_scraped=self.current_chat_id, last_text=text,
                        # )

                    if keyboard.is_pressed('esc'):
                        print("Detenido por el usuario.")
                        exit()


                else:
                    has_more = False

            if not was_handled_overflow:
                config = BOT_CONFIG[self.display_resolution]['GET_TEXTS_DID_NOT_WATCHED']
                scroll_move = config['scroll_move']
                self.scroll_chat_area(direction="up",
                                      scroll_move=scroll_move)

                await asyncio.sleep(1)

                self.take_screenshot()
                possible_text_contours = self.find_text_area_contours(use_first_contour_reference=True)
                 # possible_text_contours = self.find_text_area_contours(use_first_contour_reference=True
                 #                    if self.was_handled_overflow or not is_first_iter else False)

                # self.show_contours(contours=possible_text_contours, title='faaaaaaaak')


        # self.show_contours(contours=possible_text_contours, title='faaaaaaaak2')

        if has_more:
            iter_contours = enumerate(possible_text_contours[1:]) \
                if skip_next_contour else enumerate(possible_text_contours)

            # self.show_contours(contours=possible_text_contours[1:] \
            #     if skip_next_contour else possible_text_contours, title='dentro del bucle')

            for i, contour in iter_contours:
                is_photo = await self.is_photo_contour(contour_target=contour)
                if is_photo: continue

                x, y, w, h = cv2.boundingRect(contour)
                # area = cv2.contourArea(contour)
                # perimeter = cv2.arcLength(contour, closed=True)
                # epsilon = 0.01 * cv2.arcLength(contour, True)
                # approx = cv2.approxPolyDP(contour, epsilon, True)
                # num_vertices = len(approx)
                # hull = cv2.convexHull(contour)
                # defects = cv2.convexityDefects(contour, hull)
                # self.show_contours(contours=[contour],
                #                    title=f'area {area}, '
                #                          f'perimeter {perimeter}, '
                #                          f'num_vertices {num_vertices}, '
                #                          f'defects ')

                if skip_next_contour:
                    skip_next_contour = False
                    continue
                #
                is_top_edge_irregular = img_handler.is_top_edge_irregular(contour=contour,
                                                                            threshold=1,
                                                                            edge_margin_left=0,
                                                                            edge_margin_right=0,
                                                                            analyze_percent=100)

                is_bottom_edge_irregular = img_handler.is_bottom_edge_irregular(contour=contour,
                                                                                threshold=1,
                                                                                edge_margin_left=0,
                                                                                edge_margin_right=0,
                                                                                analyze_percent=100)

                # contour_points = largest_contour_found.squeeze()
                # y_coords = contour_points[:, 1]  # [y1, y2, y3, ...]
                # y_inferior_real = np.percentile(y_coords, 90)  # Ajusta el percentil según necesidad

                # text_contours = possible_text_contours[1:]
                # is_link = self.is_link(contour,
                #                        text_contours[i+1] if len(text_contours) > i+1 else None)

                # self.show_contours(contours=[contour],
                #                    title=f'is_top_edge_irregular {is_top_edge_irregular} '
                #                          f'is_bottom_edge_irregular {is_bottom_edge_irregular}'
                #                          f'x={x}, y={y}, w={w}, h={h}')

                if False:
                    if is_top_edge_irregular: skip_next_contour = True

                else:
                    skip_next_contour = False

                    config = BOT_CONFIG[self.display_resolution]['GET_TEXTS_DID_NOT_WATCHED']
                    x_start_offset = config['x_start_offset']
                    y_start_offset = config['y_start_offset']

                    text = self.get_text_by_text_location(
                        x_start=x - 5,
                        y_start=y + y_start_offset,
                        x_end=x + w,
                        y_end=(y + h) - 15,
                        scroll_pos_start=self.scroll_reference,
                        scroll_pos_end=self.scroll_reference,
                        desactivate_scroll=True
                    )

                    if self.is_online: await self.websocket.send_websocket_message(
                        message_type="bot_message", message=text,
                        name=self.name, current_chat_id=self.current_chat_id)

                    is_watched = self.is_text_already_watched(text=text, index=i+1)

                    if not is_watched:
                        start_location = (x, y, self.scroll_reference)
                        end_location = (x + w, y + h, self.scroll_reference)
                        texts_did_not_watched.append([start_location, end_location])

                        if is_first_iter:
                            if msg2 is None:
                                msg2 = text
                            elif msg3 is None:
                                msg3 = text
                            elif msg4 is None:
                                msg4 = text
                            elif msg5 is None:
                                msg5 = text

                    else:
                        has_more = False
                        break

                    if keyboard.is_pressed('esc'):
                        print("Detenido por el usuario.")
                        exit()

        print('is_memory_active ', self.is_memory_active)
        print('is_first_iter ' , is_first_iter)

        if self.is_memory_active and is_first_iter:
            self.add_last_five_texts_watched_v3(last_text=last_text, msg_2=msg2, msg_3=msg3,
                                                msg_4=msg4, msg_5=msg5)

        # if self.is_memory_active: self.chat_querys.update_chat_by_chat_id_scraped(
        #     id_scraped=self.current_chat_id, last_text=last_text,
        #     msg2=msg2, msg3=msg3, msg4=msg4, msg5=msg5,
        # )

        return has_more, texts_did_not_watched


    def repair_irregular_top_edge(self, image, contour,
                                  threshold=1, edge_margin=5,
                                  line_thickness=2, radius=5,
                                  offset1=-10, offset2=20):
        """
        Repara solo los segmentos irregulares del borde superior de un contorno en la imagen,
        añadiendo pequeños radios en los extremos de cada reparación. La línea superior se dibuja
        en color rojo y está ligeramente desplazada hacia la derecha.

        Args:
            image (numpy.ndarray): La imagen sobre la que se va a dibujar.
            contour (numpy.ndarray): El contorno con borde superior irregular.
            threshold (int): Umbral para considerar una diferencia significativa en 'y'.
            edge_margin (int): Margen en píxeles para excluir los bordes izquierdo y derecho.
            line_thickness (int): Grosor de la línea de reparación.
            radius (int): Radio para las esquinas redondeadas.
            offset (int): Desplazamiento en píxeles hacia la derecha para el inicio de la línea.

        Returns:
            numpy.ndarray: La imagen con los segmentos irregulares reparados.
        """
        # Hacer una copia de la imagen para no modificar la original
        result_image = image.copy()

        # Extraer los puntos del contorno
        points = contour[:, 0]  # Los puntos están almacenados como un array de shape (N, 1, 2)

        # Crear un diccionario para almacenar el valor mínimo de 'y' para cada 'x'
        top_edge_points = {}
        for x, y in points:
            if x not in top_edge_points or y < top_edge_points[x]:
                top_edge_points[x] = y

        # Convertir el diccionario en una lista ordenada por 'x'
        sorted_top_edge = sorted(top_edge_points.items(), key=lambda item: item[0])

        # Extraer las coordenadas x e y del borde superior
        x_coords = np.array([x for x, y in sorted_top_edge])
        y_coords = np.array([y for x, y in sorted_top_edge])

        # Excluir los bordes laterales según el margen especificado
        if len(x_coords) <= 2 * edge_margin:
            return result_image  # No hay suficientes puntos para analizar

        # Calcular las diferencias en Y entre puntos consecutivos
        y_diffs = np.diff(y_coords)

        # Encontrar los índices donde el borde baja significativamente
        drop_indices = np.where(y_diffs > threshold)[0] + 1  # +1 porque diff reduce el tamaño

        if len(drop_indices) == 0:
            return result_image  # No hay irregularidades significativas

        # Dividir el borde en segmentos regulares e irregulares
        segments = []
        start_idx = edge_margin

        for drop_idx in drop_indices:
            if drop_idx < edge_margin or drop_idx > len(x_coords) - edge_margin:
                continue  # Ignorar cambios cerca de los bordes

            # Segmento antes de la caída
            if start_idx < drop_idx:
                segments.append(('regular', start_idx, drop_idx))

            # Encontrar dónde termina la caída (vuelve a subir)
            end_drop_idx = drop_idx
            while end_drop_idx < len(y_coords) - 1 and y_coords[end_drop_idx + 1] >= y_coords[end_drop_idx]:
                end_drop_idx += 1

            # Segmento irregular
            segments.append(('irregular', drop_idx, end_drop_idx))
            start_idx = end_drop_idx

        # Añadir el último segmento si queda
        if start_idx < len(x_coords) - edge_margin:
            segments.append(('regular', start_idx, len(x_coords) - edge_margin))

        # Procesar cada segmento irregular
        for seg_type, start_idx, end_idx in segments:
            if seg_type == 'irregular':
                # Calcular la altura de reparación (mínimo Y en el área circundante)
                window_start = max(0, start_idx - 3)
                window_end = min(len(y_coords), end_idx + 3)
                repair_y = min(y_coords[window_start:window_end]) + 4

                # Coordenadas de los extremos del segmento irregular
                x1, y1 = x_coords[start_idx], y_coords[start_idx]
                x2, y2 = x_coords[end_idx], y_coords[end_idx]

                # Ajustar el inicio de la línea hacia la derecha
                x1_offset = x1 + offset1
                x2_offset = x2 + offset2

                # Dibujar la línea recta de reparación en color rojo
                # cv2.line(result_image, (x1_offset, repair_y), (x2_offset, repair_y), (255, 255, 255), line_thickness)
                cv2.line(result_image, (x1_offset, repair_y - 6), (x2_offset, repair_y - 6), (255, 255, 255),
                         line_thickness)
                cv2.line(result_image, (x1_offset, repair_y), (x2_offset, repair_y), (255, 255, 255), line_thickness)

                # Dibujar radios en los extremos
                # cv2.ellipse(result_image, (x1 + offset1, repair_y + radius), (radius, radius), 0, 180, 270, (0, 0, 255), line_thickness)
                # cv2.ellipse(result_image, (x2 + offset2, repair_y + radius), (radius, radius), 0, 270, 360, (0, 0, 255), line_thickness)
                break

        return result_image


    def find_closest_contour(self, contours_found):
        best_contour = None
        # NUEVA MÉTRICA: Distancia Y mínima desde el borde superior del contorno al borde superior del chat
        min_distance_y_found = float('inf')
        # Altura máxima encontrada en la distancia Y mínima (para desempate)
        max_height_at_min_y_distance = -1
        # Tolerancia para la distancia Y (pequeña, para agrupar contornos muy cercanos en Y)
        y_distance_tolerance = 10  # Píxeles - Ajusta si es necesario
        # Filtros para ignorar contornos muy pequeños (artefactos)
        min_contour_height = 10  # Ignorar contornos con altura menor a esto
        min_contour_width = 20  # Ignorar contornos con ancho menor a esto

        if not self.chat_area_reference:
            print("Error: chat_area_reference no está definido...")
            return None

        x_chat, y_chat, w_chat, h_chat = self.chat_area_reference
        chat_top_edge = y_chat  # Coordenada Y superior del área del chat

        print(f"--- Buscando contorno en overflow (Lógica v2) ---")
        print(f"Chat Area Top Edge: {chat_top_edge}")
        print(f"Tolerancia Distancia Y: {y_distance_tolerance}")
        print(f"Filtros: Altura > {min_contour_height}, Ancho > {min_contour_width}")

        if not contours_found:
            print("No se encontraron contornos después de reparar la imagen.")
            return None  # O manejar de otra forma

        for contour in contours_found:
            x, y, w, h = cv2.boundingRect(contour)

            # Aplicar filtros básicos
            if h < min_contour_height or w < min_contour_width:
                print(f"Contorno: (x={x}, y={y}, w={w}, h={h}) -> Filtrado (tamaño pequeño)")
                continue  # Ignorar contornos demasiado pequeños

            # NUEVA MÉTRICA PRIMARIA: Distancia del borde SUPERIOR del contorno al borde SUPERIOR del chat
            distance_y = abs(y - chat_top_edge)

            print(f"Contorno: (x={x}, y={y}, w={w}, h={h}), DistanciaY={distance_y:.2f}")

            # 1. ¿Es este contorno significativamente más cercano en Y que el mejor encontrado?
            if distance_y < min_distance_y_found - y_distance_tolerance:
                print(
                    f"  -> Nuevo mejor: Más cercano en Y (DistanciaY {distance_y:.2f} < {min_distance_y_found:.2f} - {y_distance_tolerance})")
                min_distance_y_found = distance_y
                max_height_at_min_y_distance = h
                best_contour = contour

            # 2. ¿Está este contorno a una distancia Y muy similar al mejor encontrado?
            elif abs(distance_y - min_distance_y_found) <= y_distance_tolerance:
                print(
                    f"  -> Similar distancia Y (abs({distance_y:.2f} - {min_distance_y_found:.2f}) <= {y_distance_tolerance})")
                # Si está a una distancia Y similar, usamos la ALTURA como desempate
                if h > max_height_at_min_y_distance:
                    print(f"    -> Mejor por altura (Altura {h} > {max_height_at_min_y_distance})")
                    # Mantenemos/actualizamos la min_distance_y_found y la altura
                    min_distance_y_found = min(distance_y, min_distance_y_found)
                    max_height_at_min_y_distance = h
                    best_contour = contour
                else:
                    print(f"    -> No mejor por altura (Altura {h} <= {max_height_at_min_y_distance})")
            else:
                # Este caso es para contornos que están más lejos en Y (más abajo) que el mejor encontrado + tolerancia
                print(
                    f"  -> Ignorado: Más lejano en Y (DistanciaY {distance_y:.2f} > {min_distance_y_found:.2f} + {y_distance_tolerance})")

        if best_contour is not None:
            x_lcf, y_lcf, w_lcf, h_lcf = cv2.boundingRect(best_contour)
            print(f"--- Contorno seleccionado para overflow (v2) ---")
            print(
                f"Contorno Final: (x={x_lcf}, y={y_lcf}, w={w_lcf}, h={h_lcf}), DistanciaY Final={min_distance_y_found:.2f}, Altura={max_height_at_min_y_distance}")
            print(f"---------------------------------------------")
            # self.show_contours(contours=[largest_contour_found], title="Contorno de Overflow Seleccionado (v2)")
        else:
            print(f"--- No se seleccionó ningún contorno para overflow (v2) ---")
            return None  # O manejar adecuadamente


        return best_contour


    async def handle_overflow_text(self, chat_contour,
                                   amount_scrolled, texts,
                                   is_initial_overflow=True,
                                   scroll_steps=True
                                   ):
        # Caso cuando hay texto desbordado (tratamiento diferente)
        # self.show_contours(contours=[chat_contour],Fre
        #                    title="chat area contour")
        result_image = self.repair_irregular_top_edge(
            image=self.current_screenshot, contour=chat_contour, offset2=300)

        contours_found = self.find_text_area_contours(image=result_image,
                                                    use_first_contour_reference=False,
                                                    take_all_texts=True)

        # self.show_contours(image=result_image,
        #                    contours=[],
        #                    title="Contornos encontrados y la imagen resultante")

        has_more = True

        # self.show_contours(contours=contours_found,
        #                    title="Contorno de Overflow Seleccionado (v2)")
        largest_contour_found = self.find_closest_contour(contours_found)  # Usamos la variable existente

        print("Largest contour found: ", largest_contour_found)


        if is_initial_overflow and self.first_contour_reference is None and largest_contour_found is not None:
            x, y, w, h = cv2.boundingRect(largest_contour_found)
            self.first_contour_reference = (x, y , w, h)
        #     self.show_contours(contours=[largest_contour_found],
        #                        title="first_contour_reference")
        #
        # self.show_contours(contours=[largest_contour_found],
        #                    title="Primer contorno de referencia papu")
        #
        # self.show_contours(contours=contours_found, title="Los contornos de La imagen reparada")
        # self.show_contours(contours=[largest_contour_found], title="El ultimo contorno de la imagen reparada")

        x_contour_overflow_end = None
        y_contour_overflow_end = None

        if contours_found is not None and largest_contour_found is not None:
            x, y, w, h = cv2.boundingRect(largest_contour_found)
            x_contour_overflow_end = x + w
            y_contour_overflow_end = y + h
            end_scroll_reference = self.scroll_reference
            self.first_contour_reference = (x, y , w, h)

        scroll_attempts = 0

        while scroll_attempts < MAX_SCROLL_ATTEMPTS:
            # self.show_contours(contours=[], title="antes de ejecutar el bucle dentro del overflow")
            scroll_attempts += 1
            x, y, w, h = cv2.boundingRect(largest_contour_found)
            steps = get_subtraction_steps(
              initial_value=y,
              target_value=y+h,
              steps=5)

            for i, step in enumerate(steps):
                step = math.ceil(abs(step))
                if i == len(steps) - 1:
                    step = math.ceil(step / 3)
                self.scroll_chat_area(direction='up',
                                      scroll_move=step)
                amount_scrolled += step
                await asyncio.sleep(1)

            self.take_screenshot()

            possible_text_contours = self.find_text_area_contours(use_first_contour_reference=False)

            if len(possible_text_contours) == 0:
                continue

            conours_found = self.find_text_area_contours(
                use_first_contour_reference=False)

            # self.show_contours(contours=conours_found,
            #                    title="find_text_area_contours")

            if not conours_found or contours_found is None or len(contours_found) <= 0:
                # self.show_contours(contours=conours_found,
                #                    title="find_text_area_contours, pero antes del break")
                break
            #
            # self.show_contours(contours=conours_found,
            #                    title="conours_found")

            contour_overflow = conours_found[0]

            # img_handler = ImgHandler(image=self.current_screenshot)
            # is_top_edge_irregular = img_handler.is_top_edge_irregular(contour=contour_overflow,
            #                                                           threshold=1,
            #                                                           edge_margin_left=0,
            #                                                           edge_margin_right=0,
            #                                                           analyze_percent=100)
            #
            # if not is_top_edge_irregular:
            #     return True
            # self.show_contours(contours=[contour_overflow],
            #                    title="contour with overflowwwwwwww")

            x, y, w, h = cv2.boundingRect(contour_overflow)
            x_contour_overflow_start = x
            y_contour_overflow_start = y
            y_contour_overflow_start_plus_h = y + h

            # await self.get_texts_did_not_watched_list(
            #     possible_text_contours=[contour_overflow]
            # )
            contour_points = largest_contour_found.squeeze()
            y_coords = contour_points[:, 1]  # [y1, y2, y3, ...]
            y_inferior_real = np.percentile(y_coords, 90)  # Ajusta el percentil según necesidad

            text = self.get_text_by_text_location(
                x_start=x_contour_overflow_start + 15,
                y_start=y_contour_overflow_start + 25,
                x_end=x_contour_overflow_end,
                y_end=y_inferior_real - 20,
                scroll_pos_start=self.scroll_reference,
                scroll_pos_end=amount_scrolled,
            )

            x, y, w, h = self.chat_area_reference
            pyautogui.click((x + w) / 2, (y + h) / 2)

            if is_initial_overflow and self.is_memory_active:
                self.add_last_five_texts_watched_v3(last_text=text)

            elif not is_initial_overflow and self.is_memory_active:
                self.add_last_five_texts_watched_v3(last_text=text, add_to_first_empty=True)


            if self.is_online: await self.websocket.send_websocket_message(
                message_type="bot_message", message=text)

            texts.append([(x_contour_overflow_start, y_contour_overflow_start, self.scroll_reference),
                          (x_contour_overflow_end, y_contour_overflow_end, end_scroll_reference)])


            is_watched = self.is_text_already_watched(text=text, index=len(texts))

            if is_watched:
                has_more = False
                return has_more


            if scroll_steps:
                steps = get_subtraction_steps(
                    initial_value=y_contour_overflow_start,
                    target_value=y_contour_overflow_start_plus_h,
                    steps=5
                )

                for i, step in enumerate(steps):
                    step = math.ceil(abs(step))
                    if i == len(steps) - 1:
                        step = math.ceil(step - step*0.1)

                    self.scroll_chat_area(direction='up',
                                          scroll_move=step)
                    await asyncio.sleep(1)

            break

        if scroll_attempts >= MAX_SCROLL_ATTEMPTS:
            raise RuntimeError("Se ha excedido el número máximo de intentos de scroll.")


        return has_more


    def is_chat_area_the_same(self, prev_chat_area_img = None, threshold = 0.8):
        """
        Verifica si el chat area de la página actual es el mismo que el del chat area anterior.

        :param prev_chat_area_img:
        :return:
        """
        self.take_screenshot()
        current_chat_area_img = self.get_chat_area_cropped()

        # img_handler = ImgHandler(image=prev_chat_area_img)
        # error = img_handler.similarity_by_mse(image=current_chat_area_img)

        result = cv2.matchTemplate(prev_chat_area_img,
                                   current_chat_area_img,
                                   cv2.TM_CCOEFF_NORMED
                                   )

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # self.show_contours(image=prev_chat_area_img, contours=[], title='prev chat area img')
        # self.show_contours(image=current_chat_area_img, contours=[], title=f'curr chat area img error= {max_val}')

        if max_val >= threshold:
            return True

        return False


    async def review_chat(
                        self, has_more: bool = True,
                        texts: List[List[Tuple[int, int, int]]] = None,
                        iterations: int = 0
    ) -> List[List[Tuple[int, int, int]]]:
        """
        This function extracts the texts into chat contour as little contours.
        Each text is returned as a contour.

        :param iterations:
        :param has_more: Flag to indicate if there are more texts to extract
        :param texts: Accumulated list of text contours
        :return: List of text contours
        """

        if not self.current_chat_id:
            pass


        if iterations > MAX_ITERATIONS:
            raise RecursionError("Se ha excedido el número máximo de iteraciones.")

        if texts is None:
            texts = []

        has_last_text = False
        last_text, _, _, _, _ = self.get_last_five_texts_by_current_chat_id()
        if last_text and (self.is_memory_active or self.is_only_check):
            has_last_text = True

        if not has_more or (not has_last_text and len(texts) >= self.messages_amount_limit):
            return texts

        self.take_screenshot()

        chat_contour = self.find_chat_area_contour()

        # self.show_contours(contours=[chat_contour], title="chat_contour")

        scrolled = 0

        # Chequear si hay overflow
        while True:
            self.take_screenshot()
            # self.show_contours(contours=[], title="testing overflow")
            is_overflow = self.is_there_text_overflow(chat_contour=chat_contour)
            if not is_overflow:
                break
            possible_text_contours = self.find_text_area_contours()

            # self.show_contours(contours=possible_text_contours,
            #                    title="first checker contours possible text contours")

            if is_overflow and len(possible_text_contours) == 0:
                has_more = await self.handle_overflow_text(chat_contour=chat_contour,
                                                amount_scrolled=scrolled,
                                                texts=texts, is_initial_overflow=not self.was_handled_overflow,
                                                scroll_steps=True)

                self.was_handled_overflow = True
                scrolled = 0
                if not has_more or (not has_last_text and len(texts) >= self.messages_amount_limit):
                    return texts
            else:
                break

            await asyncio.sleep(1)

        # self.show_contours(contours=[chat_contour], title="sali del bucle del overflow")

        if not self.was_handled_overflow:
            self.take_screenshot()
            possible_text_contours = self.find_text_area_contours(use_first_contour_reference=False)
            # self.show_contours(contours=possible_text_contours,
            #                    title="possible text contour")
            # self.show_contours(contours=[possible_text_contours[0]],
            #                    title="last possible text contour")
            all_texts_contours = self.find_text_area_contours(take_all_texts=True,
                                                              use_first_contour_reference=False)
            # self.show_contours(contours=all_texts_contours,
            #                    title="all texts contour")
            # self.show_contours(contours=[all_texts_contours[0]],
            #                    title="last all texts contour")

            if len(possible_text_contours) > 1 and len(all_texts_contours) > 1:
                # self.show_contours(contours=possible_text_contours,
                #                    title="possible text contour")
                # self.show_contours(contours=all_texts_contours,
                #                    title="all texts contour")
                x_1, y_1, w_1, h_1 = cv2.boundingRect(possible_text_contours[0])
                x_2, y_2, w_2, h_2 = cv2.boundingRect(all_texts_contours[0])

                if w_2 != w_1 and iterations == 0:
                    config = BOT_CONFIG[self.display_resolution]['REVIEW_CHAT']
                    scroll_move = config['scroll_move']

                    self.scroll_chat_area(direction="up",
                                          scroll_move=scroll_move)
                    await asyncio.sleep(1)

        await asyncio.sleep(1)
        self.take_screenshot()
        possible_text_contours = self.find_text_area_contours(
            use_first_contour_reference=True if self.was_handled_overflow or iterations > 0 else False)
        #
        # self.show_contours(contours=possible_text_contours,
        #                    title="possible text contour")

        # self.show_contours(contours=possible_text_contours,
        #                    title="possible text contour")
        # self.show_contours(contours=all_texts_contours,
        #                    title="all texts contour")

        # self.show_contours(contours=possible_text_contours,
        #                    title="Testeando todos los contornos posibles al inicio de la funcion cuando se hace scroll.")

        # self.show_contours(contours=possible_text_contours,
        #                    title=f"Testeando todos los contornos posibles al inicio de la funcion. use_first_contour_reference={aver}")

        if chat_contour is None or not isinstance(chat_contour, np.ndarray):
            raise ValueError("No se pudo obtener el contorno del chat.")

        if not possible_text_contours or not isinstance(possible_text_contours, list):
            return texts

        x, y, w, h = cv2.boundingRect(chat_contour)
        self.chat_area_reference = (x, y, w, h)

        has_more_text, texts_did_not_watched = await self.get_texts_did_not_watched_list(
            possible_text_contours=possible_text_contours,
            is_first_iter=iterations == 0,
            texts=texts,
            was_handled_overflow=self.was_handled_overflow

        )
        # if not texts_did_not_watched: return

        texts += texts_did_not_watched

        if has_more_text:
            if len(texts) > 0:
                # current_chat_area_img = self.get_chat_area_cropped()
                #
                # self.scroll_chat_area(direction='up',
                #                       scroll_move=50)
                # await asyncio.sleep(1)
                #
                # is_chat_area_the_same = self.is_chat_area_the_same(
                #     prev_chat_area_img=current_chat_area_img)
                #
                # if is_chat_area_the_same:
                #     return texts

                # self.scroll_chat_area(direction='down',
                #                       scroll_move=50)
                # await asyncio.sleep(1)

                steps = get_subtraction_steps(
                    initial_value=texts[-1][0][1],
                    target_value=self.first_contour_reference[1]+self.first_contour_reference[-1]
                        if self.first_contour_reference is not None else 0,
                    steps=10
                    )

                prev_chat_area_img = self.get_chat_area_cropped()

                for i, step in enumerate(steps):
                    step = math.ceil(abs(step))
                    if i == len(steps) - 1:
                        step = math.ceil(step / 3)

                    self.scroll_chat_area(direction='up',
                                          scroll_move=step)
                    await asyncio.sleep(1)

                    is_chat_area_the_same = self.is_chat_area_the_same(
                        prev_chat_area_img=prev_chat_area_img)

                    if is_chat_area_the_same:
                        return texts

                    prev_chat_area_img = self.get_chat_area_cropped()


            # Después de hacer scroll (en cualquier caso), volvemos a llamar a la función
            return await self.review_chat(
                has_more=has_more,
                texts=texts,
                iterations=iterations+1
            )

        return texts


    def get_text_by_text_location(self, x_start, y_start, x_end,
                                  y_end, scroll_pos_start, scroll_pos_end,
                                  desactivate_scroll=False, duration=0) -> str | None:

        # if not desactivate_scroll: self.scroll_chat_area(
        #     direction="up" if scroll_pos_start > self.scroll_reference else "down",
        #     scroll_move=scroll_pos_start,
        #     move_to_chat = False
        # )

        # def move_gradually(start_x, start_y, end_x, end_y, steps=20, duration=0.5):
        #     current_x, current_y = start_x, start_y
        #     step_x = (end_x - start_x) / steps
        #     step_y = (end_y - start_y) / steps
        #
        #     for i in range(steps):
        #         current_x += step_x
        #         current_y += step_y
        #         pyautogui.moveTo(int(current_x), int(current_y), duration=duration/steps)
        #
        #
        # current_x, current_y = pyautogui.position()
        #
        # move_gradually(current_x, current_y, x_start, y_start)

        pyautogui.moveTo(x=x_start, y=y_start, duration=duration)

        pyautogui.doubleClick(button="left")
        pyautogui.mouseDown(button="left")

        pyautogui.moveTo(x=x_end, y=y_end, duration=duration)

        if not desactivate_scroll:
            self.scroll_chat_area(
                direction="down",
                scroll_move=scroll_pos_end,
                move_to_chat=False
            )
            time.sleep(1)

        pyperclip.copy(None)
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.mouseUp(button="left")

        if not desactivate_scroll:
            self.scroll_chat_area(
                direction="up",
                scroll_move=scroll_pos_end,
                move_to_chat=False
            )
            time.sleep(1)

        return pyperclip.paste()

        """
        Alternativa
        pyautogui.click(x=x_start, y=y_start, duration=0.3)
        pyautogui.keyDown("shift")
        pyautogui.click(x=x_end, y=y_end, duration=0.3)
        pyautogui.keyUp("shift")
        pyautogui.hotkey('ctrl', 'c')
        return pyperclip.paste()
        """


    def find_option_button_contour(self):
        chats_contour = self.take_chats_container_contour()
        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)
        min_distance = float('inf')  # Inicializar con un valor muy grande
        closest_contour = None
        valid_contours = []

        # Definir límites para filtrar la esquina superior derecha
        y_top_limit = y_chats + int(h_chats * 0.2)  # Primer 20% en Y (parte superior)
        x_right_half = x_chats + int(w_chats * 0.5)  # Mitad derecha en X

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Verificar si el contorno está dentro de la zona superior derecha del área de chats
            is_in_top_y = y < y_top_limit
            is_in_right_x = x > x_right_half

            # Verificar si está dentro del área general de los chats (opcional pero recomendable)
            is_inside_chats_area = (
                    x_chats <= x <= x_chats + w_chats and
                    y_chats <= y <= y_chats + h_chats
            )

            # Filtrar por tamaño
            size_ok = 20 < w < 60 and h > 20

            if is_inside_chats_area and is_in_top_y and is_in_right_x and size_ok:
                valid_contours.append(contour)


        for contour in valid_contours:
            x, y, w, h = cv2.boundingRect(contour)

            distance = abs(x - x_chats)

            # Si este contorno está más cerca que los anteriores, actualizar
            if distance < min_distance:
                min_distance = distance
                closest_contour = contour

        return closest_contour


    def find_message_requests_cords(self, x_btn, y_btn, h_btn):
        x_cord = x_btn + 50
        y_cord = (y_btn+h_btn)*2
        return (x_cord, y_cord)


    def go_to_message_requests_view(self):
        btn_contour = self.find_option_button_contour()
        x, y, w, h = cv2.boundingRect(btn_contour)
        x_cord, y_cord = self.find_message_requests_cords(x, y, h)

        pyautogui.click(x + w/2, y + h/2, duration=1)
        time.sleep(1)

        pyautogui.click(x_cord, y_cord, duration=1)
        time.sleep(1)

        # self.is_in_message_requests_view = True
        self.bot_querys.update_bot(name=self.name, is_in_message_requests_view=True)


    def go_to_principal_view(self):
        back_button_contour = self.find_back_arrow_contour()

        x, y, w, h = cv2.boundingRect(back_button_contour)
        pyautogui.click(x+20, y, duration=1)
        time.sleep(1)

        # self.is_in_message_requests_view = False
        self.bot_querys.update_bot(name=self.name, is_in_message_requests_view=False)


    def is_in_principal_view(self):
        self.take_screenshot()
        chats_contour = self.take_chats_container_contour()
        if chats_contour is None:
            return False

        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()

        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

        # Definir límites para filtrar la esquina superior derecha
        y_top_limit = y_chats + int(h_chats * 0.2)  # Primer 20% en Y (parte superior)
        x_right_half = x_chats + int(w_chats * 0.5)  # Mitad derecha en X

        valid_contours = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Verificar si el contorno está dentro de la zona superior derecha del área de chats
            is_in_top_y = y < y_top_limit
            is_in_right_x = x > x_right_half

            # Verificar si está dentro del área general de los chats (opcional pero recomendable)
            is_inside_chats_area = (
                    x_chats <= x <= x_chats + w_chats and
                    y_chats <= y <= y_chats + h_chats
            )

            # Filtrar por tamaño
            size_ok = 20 < w < 60 and h > 20

            if is_inside_chats_area and is_in_top_y and is_in_right_x and size_ok:
                valid_contours.append(contour)

        # self.show_contours(contours=valid_contours,
        #                    title=f'is in principal view {len(valid_contours) > 1}')

        # Devolver True si hay más de un contorno válido
        return len(valid_contours) > 1


    def is_in_request_view(self):
        self.take_screenshot()
        chats_contour = self.take_chats_container_contour()
        if chats_contour is None:
            return False

        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()

        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

        # Definir límites para filtrar la esquina superior derecha
        y_top_limit = y_chats + int(h_chats * 0.2)  # Primer 20% en Y (parte superior)
        x_right_half = x_chats + int(w_chats * 0.5)  # Mitad derecha en X

        valid_contours = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Verificar si el contorno está dentro de la zona superior derecha del área de chats
            is_in_top_y = y < y_top_limit
            is_in_right_x = x > x_right_half

            # Verificar si está dentro del área general de los chats (opcional pero recomendable)
            is_inside_chats_area = (
                    x_chats <= x <= x_chats + w_chats and
                    y_chats <= y <= y_chats + h_chats
            )

            # Filtrar por tamaño
            size_ok = 20 < w < 60 and h > 20

            if is_inside_chats_area and is_in_top_y and is_in_right_x and size_ok:
                valid_contours.append(contour)

        # self.show_contours(contours=valid_contours,
        #                    title=f'is in principal view {len(valid_contours) > 1}')

        # Devolver True si hay más de un contorno válido
        return len(valid_contours) == 1


    def find_back_arrow_contour(self):
        chats_contour = self.take_chats_container_contour()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)
        img_handler = ImgHandler(image=self.current_screenshot)
        contours = img_handler.find_contours_by_large_contours_mask()
        min_combined_distance = float('inf')
        closest_contour = None

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Verificar si está dentro del área de chats
            if x_chats + w_chats > x > x_chats and y_chats + h_chats > y > y_chats:
                # Calcular distancias normalizadas (para evitar sesgo por diferencias de escala)
                norm_distance_x = abs(x - x_chats) / w_chats  # Distancia X normalizada
                norm_distance_y = abs(y - y_chats) / h_chats  # Distancia Y normalizada

                # Combinación de distancias (50% peso para cada eje)
                combined_distance = 0.5 * norm_distance_x + 0.5 * norm_distance_y

                # Mantener el contorno más cercano
                if combined_distance < min_combined_distance:
                    min_combined_distance = combined_distance
                    closest_contour = contour

        return closest_contour


    def get_chat_area_cropped(self):
        chat_area = self.find_chat_area_contour()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chat_area)
        cropped = self.current_screenshot[y_chats:y_chats+h_chats, x_chats:x_chats+w_chats]
        return cropped


    async def run(self):
        if self.is_online: await self.websocket.establish_connection()
        counter = 0

        chats_scrroll_done = False

        print("Running...")
        last_print = ""

        # if not self.is_in_principal_view():
        #     self.go_to_principal_view()

        while True:
            print("buscando chats o lo que surja")
            try:
                if keyboard.is_pressed('esc'):
                    print("Detenido por el usuario.")
                    exit()
                # pyautogui.keyDown('F11')
                self.take_screenshot()
                is_target = self.is_watching_target_v2()

                if (not self.window_handler.is_window_maximized() or
                        self.window_handler.is_window_maximized() and not is_target):
                    maximized = self.window_handler.maximize_window()

                    await asyncio.sleep(2)

                    self.take_screenshot()
                    is_target = self.is_watching_target_v2()

                    # self.show_contours(contours=[], title=f"is_target {is_target} maximized {maximized}")

                    if maximized and not is_target:
                        await asyncio.sleep(1)

                        # if self.window_handler.is_window_maximized():
                        screen_width, screen_height = pyautogui.size()
                        pyautogui.moveTo(screen_width/2, screen_height/2)
                        pyautogui.keyDown('F11')
                        await asyncio.sleep(8)


                if not is_target:
                    # Si no estamos viendo el objetivo, imprimir "No Watching target..."
                    # print("                                                             ",
                    #       end="\r", flush=True)
                    # print("No Watching target...", end="\r", flush=True)
                    # last_print = "nowatch"
                    print('no watching')
                    continue
                else:
                    # Si estamos viendo el objetivo, imprimir "Watching target {self.target_name}..."
                    # print("                                                             ",
                    #       end="\r", flush=True)
                    # print(f"Watching target {self.target_name}...", end="\r", flush=True)
                    # last_print = "watching"
                    print('watching')
                    pass

                if counter > 2 or counter < 2:
                    if self.is_in_principal_view():
                        pass
                    else:
                        self.go_to_principal_view()

                else:
                    if self.is_in_principal_view():
                        counter = 0
                        self.go_to_message_requests_view()

                    else:
                        counter = 0
                        self.go_to_principal_view()

                print(f"Counter: {counter}")

                counter += 1

                self.scroll_chats_area(direction='up',
                                       scroll_move=10_000)
                self.chats_area_scroll_reference = 0

                review_each_view_counter = 1

                while review_each_view_counter <= 5:
                    if review_each_view_counter == 2 and not self.is_in_principal_view():
                        break

                    lookup_chats_counter = 0
                    order_chats_ids: List[str] = []
                    order_cursor = 0

                    chats = self.find_chat_references()

                    # Obtener orden de referencia de chats a seguir
                    if lookup_chats_counter == 0:
                        for chat in chats:
                            x, y, _, _ = cv2.boundingRect(chat)
                            chat_id = self.extract_chat_id(chat_ref=(x, y))
                            # self.show_contours(contours=[], title=f'chat id -> {chat_id}')
                            order_chats_ids.append(chat_id)


                    lookup_chats_counter += 1

                    if chats is not None and len(chats) > 0:
                        self.amount_of_time_chats_area_down_scrolled = 0

                        button_contour = self.find_button_to_bottom_contour()

                        if button_contour is not None:
                            x, y, w, h = cv2.boundingRect(button_contour)
                            pyautogui.click(x=x+w/2, y=y+h/2)

                        else:
                            self.scroll_chat_area(direction='down', scroll_move=1_000_000)

                        print("entra a iterar los chats...")
                        for chat in chats[::-1]:
                            x, y, _, _ = cv2.boundingRect(chat)

                            chat_id = self.extract_chat_id(chat_ref=(x, y))
                            chat_id_reference = order_chats_ids[order_cursor]

                            if chat_id != chat_id_reference:
                                continue

                            self.click_chat(chat_ref=(x, y), duration=1)

                            if chat_id:
                                chat = self.chat_querys.get_chat_by_id_scraped(
                                    id_scraped=chat_id)

                                if not chat:
                                    self.chat_querys.create_chat(id_scraped=chat_id)

                           # self.move_to_chat()
                            self.take_screenshot()
                            await self.review_chat()

                            self.chat_querys.update_chat_by_chat_id_scraped(id_scraped=self.current_chat_id,
                                                                            last_text_url=None, last_text_index=0,
                                                                            **self.last_five_texts_memory_db_v2)

                            self.clear_texts_not_watched_v2()

                            self.was_handled_overflow = False

                            self.scroll_chat_area(direction='down',
                                                   scroll_move=self.scroll_reference)
                            self.scroll_reference = 0

                            await asyncio.sleep(1)
                            chats = self.find_chat_references()
                            order_cursor += 1

                        x, y, w, h = cv2.boundingRect(self.chats_reference)
                        self.scroll_chats_area(direction='down', scroll_move=int(h * 0.50))

                    else:
                        # Si ya he bajado 3 veces y no he visto nada entonces subo completo
                        # en caso contrario bajar
                        print('chats_area_scroll_reference ', self.chats_area_scroll_reference)
                        self.scroll_chats_area(direction='up',
                                               scroll_move=self.chats_area_scroll_reference)

                        self.chats_area_scroll_reference = 0


                        order_chats_ids.clear()
                        order_cursor = 0

                        await asyncio.sleep(0.5)

                        if review_each_view_counter % 2 != 0:
                            review_each_view_counter += 1
                            continue

                        print("pasamos a review chats")
                        self.take_screenshot()

                        if self.current_chat_id is None:
                            chat_id = self.find_current_chat_id()
                            if chat_id:
                                chat = self.chat_querys.get_chat_by_id_scraped(
                                    id_scraped=chat_id)

                                if not chat:
                                    self.chat_querys.create_chat(id_scraped=chat_id)

                            else: continue

                        button_contour = self.find_button_to_bottom_contour()

                        if button_contour is not None:
                            x, y, w, h = cv2.boundingRect(button_contour)
                            pyautogui.click(x=x+w/2, y=y+h/2)

                        self.scroll_chat_area(direction='down', scroll_move=1_000_000)

                        # await asyncio.sleep(1)
                        # self.take_screenshot()
                        print("antes del review chat")
                        await self.review_chat()

                        print("last_five_texts_memory_db_v2 ", self.last_five_texts_memory_db_v2)

                        self.chat_querys.update_chat_by_chat_id_scraped(id_scraped=self.current_chat_id,
                                                                        last_text_url=None, last_text_index=0,
                                                                        **self.last_five_texts_memory_db_v2)

                        self.clear_texts_not_watched_v2()
                        self.was_handled_overflow = False
                        self.scroll_chat_area(direction='down',
                                              scroll_move=self.scroll_reference)
                        self.scroll_reference = 0

                    review_each_view_counter += 1


            # if self.is_in_message_requests_view:
            #     self.go_to_principal_view()

            except Exception as e:
                print(f'Error raised: {e}')

            finally:
                continue


    async def turn_on(self):
        asyncio.create_task(self.websocket.establish_connection())
        await self.run()
        # await asyncio.gather(
        #     self.websocket.establish_connection(),
        #     self.run()
        # )

