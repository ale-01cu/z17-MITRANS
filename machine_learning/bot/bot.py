import numpy as np
import pyautogui
import cv2
from img_handler import ImgHandler
from img_to_text import img_to_text
import time
from db.chat_querys import ChatQuerys
import pyperclip
from typing import List, Tuple
import os

# dirname = os.path.dirname(__file__)
# image_path = os.path.join(dirname, 'Captura de pantalla 2025-03-30 114247.png')
# image_test = cv2.imread(image_path)

MAX_ITERATIONS = 100  # Ejemplo de límite
MAX_SCROLL_ATTEMPTS = 50  # Ejemplo de límite

# Add these imports at the top of the file
import asyncio
from websocket_client import WebSocketClient

class Bot:
    def __init__(self, name: str, target_name: str, target_templates_paths: list[str], websocket_uri: str) -> None:
        self.name = name
        self.target_name = target_name

        self.previous_screenshot = None
        self.chats_reference = None
        self.chat_area_reference = None
        self.current_chat_id = None
        self.current_screenshot = None
        self.last_circles_references_detected = None
        self.target_templates_paths = target_templates_paths
        self.scroll_reference = 0 # Cuanto se ha desplazado el scroll desde el fondo.
        # self.target_template = cv2.imread(self.target_template_path)
        self.chat_querys = ChatQuerys()

        # Initialize WebSocket client
        self.websocket = WebSocketClient(
            uri=websocket_uri,
            on_message=self.handle_websocket_message
        )
        self.websocket_uri = websocket_uri


    async def connect_websocket(self):
        """Connects to the WebSocket server"""
        return await self.websocket.connect()

    async def disconnect_websocket(self):
        """Disconnects from the WebSocket server"""
        await self.websocket.disconnect()

    async def send_websocket_message(self, message_type: str, data: dict):
        """Sends a message through the WebSocket connection"""
        message = {
            "type": message_type,
            "data": data,
            "bot_name": self.name,
            "timestamp": time.time()
        }
        return await self.websocket.send_message(message)


    async def handle_websocket_message(self, message: dict):
        """Handles incoming WebSocket messages"""
        try:
            message_type = message.get("type")
            data = message.get("data")

            if message_type == "command":
                # Handle different commands
                if data.get("action") == "stop":
                    # Handle stop command
                    pass
                elif data.get("action") == "start":
                    # Handle start command
                    pass
                # Add more command handlers as needed

        except Exception as e:
            print(f"Error handling WebSocket message: {e}")


    async def establish_connection(self):
        """Asynchronous version of the run method"""
        print("Running async...")
        
        # Connect to WebSocket server
        if not await self.connect_websocket():
            print("Failed to connect to WebSocket server")
            return

        try:
            # Send status update through WebSocket
            await self.send_websocket_message("status", {
                "ok": True,
            })

        except Exception as e:
            print(f"Error in run_async: {e}")


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


    def find_text_area_contours(self, image = None):
        img_handler = ImgHandler(image=self.current_screenshot if image is None else image)
        contours = img_handler.find_contours_by_large_contours_mask()
        possible_text_contours = []
        chat_contour = self.find_chat_area_contour()

        x_chat, y_chat, w_chat, h_chat = cv2.boundingRect(chat_contour)

        # cv2.drawContours(self.current_screenshot, chat_contour, -1, (0, 255, 0), 3)
        # cv2.imshow('chats contour', self.current_screenshot)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filtro de tamaño (ajusta según necesidad)
            if (50 < w < 600) and (h < 50):
                # Verifica si está DENTRO del chat_contour
                if ((x > x_chat) and (x + w < x_chat + w_chat)) and ((y > y_chat) and (y + h < y_chat + h_chat)):
                    possible_text_contours.append(contour)


        # cv2.drawContours(self.current_screenshot, possible_text_contours, -1, (0, 255, 0), 3)
        # cv2.imshow('chats contour', self.current_screenshot)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return possible_text_contours


    # TODO: Agregar que encuentre los puentos dentro del contorno donde van los chats
    # para achicar el cerco y disminuir el error
    def find_chat_references(self):
        img_handler = ImgHandler(image=self.current_screenshot)
        edged = img_handler.get_edged()
        contours = img_handler.find_contours(image=edged)
        chats_contour = self.take_chats_container_contour()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)


        # x_limit = int(x_chats + 0.80 * w_chats)
        # cv2.line(self.current_screenshot, (x_limit, 0),
        #          (x_limit, self.current_screenshot.shape[0]),
        #          (0, 0, 255), 2)  # Línea roja
        # cv2.imshow('chats contour line', self.current_screenshot)
        # cv2.waitKey(0)


        # cv2.drawContours(self.current_screenshot, chats_contour, -1, (0, 255, 0), 3)
        # cv2.imshow('chats contour', self.current_screenshot)
        # cv2.waitKey(0)

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
                        x > (x_chats + 0.30 * w_chats) and x < (x_chats + w_chats) and
                        (y > y_chats and y > (y_chats + 0.10 * h_chats))
            )



            is_in_size_range = (
                (12 < w < 20) and (12 < h < 20) and w == h
            )

            # Filtrar contornos basados en la circularidad (ajusta el umbral según sea necesario)
            if 0.7 < circularity <= 1.0 and is_into_chats_contour and is_in_size_range:  # Umbral de circularidad
                contours_found.append(contour)

        # print(len(contours_found))
        # cv2.drawContours(self.current_screenshot, contours_found, -1, (0, 255, 0), 3)
        # cv2.imshow('chats mark', self.current_screenshot)
        # cv2.waitKey(0)

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
        text_roi = image[circle_y - 50:circle_y + 10, circle_x - 300:circle_x]

        # cv2.imshow('text_roi', text_roi)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

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

        pyautogui.moveTo(x=x_chats + w_chats / 2,
                         y=y_chats + h_chats / 2,
                         duration=0.3
                         )


    def scroll_chat_area(self, direction='up', scroll_move=100, move_to_chat=True):
        chat_area = self.find_chat_area_contour()
        x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chat_area)

        if move_to_chat: 
            x_pos = x_chats + w_chats / 2
            y_pos = y_chats + h_chats / 2
            pyautogui.moveTo(x=x_pos, y=y_pos,
                            duration=1)
            pyautogui.leftClick(x=x_pos, y=y_pos)


        if self.scroll_reference is None:
            self.scroll_reference = scroll_move
        elif direction == 'up' and self.scroll_reference is not None:
            self.scroll_reference += scroll_move
        elif direction == 'down' and self.scroll_reference is not None:
            self.scroll_reference -= scroll_move

        if direction == 'up':
            pyautogui.scroll(scroll_move)
        elif direction == 'down':
            pyautogui.scroll(scroll_move)

        


    def get_last_chat_id_image(self) -> ImgHandler:
        """
        Extrae el texto del último chat id detectado.

        :return: Texto del último chat id detectado.
        """
        chat_data = self.chat_querys.get_chat_by_id_scraped(
            id_scraped=self.current_chat_id)
        img_handler = ImgHandler(image=chat_data.last_text_url)
        return img_handler


    def get_last_chat_id_text(self) -> str | None:
        """
        Extrae el texto del último chat id detectado.

        :return: Texto del último chat id detectado.
        """
        chat_data = self.chat_querys.get_chat_by_id_scraped(
            id_scraped=self.current_chat_id)

        print("chat_data: ", chat_data)
        if not chat_data: return None
        return chat_data.last_text


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


    def is_there_text_overflow(self, chat_contour):
        img_handler = ImgHandler(image=self.current_screenshot)
        is_overflow = img_handler.is_top_edge_irregular(contour=chat_contour,
                                                        analyze_percent=25)
        return is_overflow


    def is_contour_already_watched(self, contour) -> bool:
        img_handler = self.get_last_chat_id_image()
        contour_image = img_handler.contour_to_image(contour=contour)
        similarity_error = img_handler.similarity_by_mse(image=contour_image)

        if similarity_error < 0.1:
            return True
        return False


    def is_text_already_watched(self, text: str) -> bool:
        """
        Comprueba si el texto ya ha sido visto por el chat id actual.

        :param text: Texto a comprobar.
        :return: True si el texto ya ha sido visto, False en caso contrario.
        """
        last_text = self.get_last_chat_id_text()
        print("prrrrrrrrrrrrrrrr")
        print("last text ", last_text)
        print("text ", text)

        if last_text == text:
            return True
        return False


    def show_contours(self, contours, title: str = "title", image = None):
        image_copy = self.current_screenshot.copy() if image is None else image.copy()
        cv2.drawContours(image_copy if image is None else image,
                         contours, -1, (0, 255, 0), 3)
        cv2.imshow(title, image_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    async def get_texts_did_not_watched_list(self, possible_text_contours):
        texts_did_not_watched = []
        has_more = True
        last_text = None

        if possible_text_contours is None:
            return has_more, texts_did_not_watched

        self.move_to_chat()

        # self.show_contours(contours=possible_text_contours, 
        # title="posible contornos de texts")

        for i, contour in enumerate(possible_text_contours):
            # Comparar img_roi con la ultima referencia del texto visto por el current chat id
            x, y, w, h = cv2.boundingRect(contour)

            # self.show_contours(contours=[contour])

            text = self.get_text_by_text_location(
                x_start=x + 10,
                y_start=y + 10,
                x_end=x + w,
                y_end=(y + h)- 10,
                scroll_pos_start=self.scroll_reference,
                scroll_pos_end=self.scroll_reference,
                desactivate_scroll=True
            )
            
            # Send the extracted text through WebSocket
            await self.send_websocket_message("new_text", {
                "chat_id": self.current_chat_id,
                "text": text,
            })

            is_watched = self.is_text_already_watched(text=text)

            if not is_watched:
                start_location = (x, y, self.scroll_reference)
                end_location = (x + w, y + h, self.scroll_reference)
                texts_did_not_watched.append([start_location, end_location])

                if i == 0:
                    last_text = text
            else:
                has_more = False
                break

        # self.chat_querys.update_chat_by_chat_id_scraped(
        #     id_scraped=self.current_chat_id, last_text=last_text)

        return has_more, texts_did_not_watched


    def repair_irregular_top_edge(self, image, contour, threshold=1, edge_margin=5, line_thickness=2, radius=5, offset1=-10,
                                  offset2=20):
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


    async def review_chat(
            self, has_more: bool = True,
            texts: List[List[Tuple[int, int, int]]] = None,
            iterations: int = 0
    ) -> List[List[Tuple[int, int, int]]]:
        """
        This function extracts the texts into chat contour as little contours.
        Each text is returned as a contour.

        :param has_more: Flag to indicate if there are more texts to extract
        :param texts: Accumulated list of text contours
        :return: List of text contours
        """
        if iterations > MAX_ITERATIONS:
            raise RecursionError("Se ha excedido el número máximo de iteraciones.")

        if texts is None:
            texts = []

        if not has_more:
            return texts

        chats_contour = self.take_chats_container_contour()
        chat_contour = self.find_chat_area_contour()
        possible_text_contours = self.find_text_area_contours()

        self.take_screenshot()
        print("chats_contour: ", len(chats_contour))
        print("chat_contour: ", len(chat_contour))
        print("pssible text contour: ", len(possible_text_contours))

        if chat_contour is None or not isinstance(chat_contour, np.ndarray):
            raise ValueError("No se pudo obtener el contorno del chat.")

        if not possible_text_contours or not isinstance(possible_text_contours, list):
            raise ValueError("No se encontraron contornos de texto posibles.")

        x, y, w, h = cv2.boundingRect(chat_contour)
        self.chat_area_reference = (x, y, w, h)

        has_more, texts_did_not_watched = await self.get_texts_did_not_watched_list(
            possible_text_contours=possible_text_contours
        )

        print("has_more: ", has_more)
        print("texts_did_not_watched: ", texts_did_not_watched)

        if has_more:
            # Si no se encuentra el último texto visto
            is_overflow = self.is_there_text_overflow(chat_contour=chat_contour)

            print("is overflow: ", is_overflow)
            # self.show_contours(contours=[chat_contour],
            #                    title="chat area contour")
            amount_scrolled = 0

            if is_overflow:
                # Caso cuando hay texto desbordado (tratamiento diferente)
                result_image = self.repair_irregular_top_edge(
                    image=self.current_screenshot, contour=chat_contour)

                chat_contour = self.find_chat_area_contour(image=result_image)

                contours = self.find_text_area_contours()

                # self.show_contours(image=result_image,
                #                    contours=contours,
                #                    title="chat area repaired")


                img_handler = ImgHandler(image=result_image)
                conours_found = img_handler.find_contours_by_large_contours_mask()

                x_contour_overflow_end = None
                y_contour_overflow_end = None

                if conours_found is not None and len(conours_found) > 0:
                    contour_overflow = conours_found[0]
                    x, y, w, h = cv2.boundingRect(contour_overflow)
                    x_contour_overflow_end = x + w
                    y_contour_overflow_end = y + h

                scroll_attempts = 0

                # looking for the start of the overflow contour
                while scroll_attempts < MAX_SCROLL_ATTEMPTS:
                    self.scroll_chat_area(direction="up", scroll_move=2)
                    amount_scrolled += 2
                    self.take_screenshot()

                    img_handler = ImgHandler(image=self.current_screenshot)
                    contours = img_handler.find_contours_by_large_contours_mask()

                    # self.show_contours(contours=contours, 
                    #                    title="todos los contornos a ver que bola"
                    #                    )

                    chat_contour = self.find_chat_area_contour()
                    # print("aaaaaaaaaaaaaaaaaaaa que locura es esta aaaa: ", len(chat_contour))
                    if chat_contour is None: 
                        continue
                    is_overflow = self.is_there_text_overflow(chat_contour=chat_contour)


                    if not is_overflow:
                        # self.show_contours(contours=[chat_contour], title="imagen sin overflow")
                        # result_image = self.repair_irregular_top_edge(
                        #     image=self.current_screenshot, contour=chat_contour)

                        # self.show_contours(image=result_image, 
                        #                    contours=[], 
                        #                    title="imagen sin overflow reparada"
                        #                    )

                        img_handler = ImgHandler(image=self.current_screenshot)
                        conours_found = img_handler.find_contours_by_large_contours_mask()

                        # self.show_contours(contours=conours_found,
                        #                    title="Contornos en el final del texto con overflow")

                        if not conours_found: raise ValueError(
                            "No se encontraron contornos válidos "
                            "después de reparar el borde superior.")

                        contour_overflow = conours_found[0]
                        x, y, w, h = cv2.boundingRect(contour_overflow)
                        x_contour_overflow_start = x
                        y_contour_overflow_start = y

                        self.get_texts_did_not_watched_list(
                            possible_text_contours=[conours_found[0]]
                        )

                        texts.append([(x_contour_overflow_start, y_contour_overflow_start, self.scroll_reference),
                                      (x_contour_overflow_end, y_contour_overflow_end, self.scroll_reference)])
                        break


                if scroll_attempts >= MAX_SCROLL_ATTEMPTS:
                    raise RuntimeError("Se ha excedido el número máximo de intentos de scroll.")

            # Caso normal: hacer scroll y continuar el proceso
            if len(texts) > 0:
                print("texts: ", texts)
                print("the las one bro: ", texts[-1])
                last_height = texts[-1][0][1] - texts[-1][1][1]

                for i in range(4):
                    self.scroll_chat_area(direction="up",
                                        scroll_move=int((self.chat_area_reference[-1] * 0.25)))
                    time.sleep(1)

            # Después de hacer scroll (en cualquier caso), volvemos a llamar a la función
            return self.review_chat(
                has_more=has_more,
                texts=texts + texts_did_not_watched,
                iterations=iterations+1
            )

        return texts + texts_did_not_watched



    def get_text_by_text_location(self, x_start, y_start, x_end,
                                  y_end, scroll_pos_start, scroll_pos_end,
                                  desactivate_scroll=False) -> str | None:

        if not desactivate_scroll: self.scroll_chat_area(
            direction="up" if scroll_pos_start > self.scroll_reference else "down",
            scroll_move=scroll_pos_start,
            move_to_chat = False
        )

        pyautogui.moveTo(x=x_start, y=y_start)

        pyautogui.doubleClick(button="left")
        pyautogui.mouseDown(button="left")

        if not desactivate_scroll: self.scroll_chat_area(
            direction="down",
            scroll_move=scroll_pos_end,
            move_to_chat=False)
        pyautogui.moveTo(x=x_end, y=y_end)

        pyperclip.copy(None)
        pyautogui.hotkey('ctrl', 'c')
        pyautogui.mouseUp(button="left")
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



    async def run(self):
        await self.establish_connection() 

        print("Running...")
        last_print = ""

        while True:
            # pyautogui.keyDown('F11')
            self.take_screenshot()
            is_target = self.is_watching_target()

            if not is_target:
                # # Si no estamos viendo el objetivo, imprimir "No Watching target..."
                # print("                                                             ",
                #       end="\r", flush=True)
                # print("No Watching target...", end="\r", flush=True)
                # last_print = "nowatch"
                continue
            else:
                # # Si estamos viendo el objetivo, imprimir "Watching target {self.target_name}..."
                # print("                                                             ",
                #       end="\r", flush=True)
                # print(f"Watching target {self.target_name}...", end="\r", flush=True)
                # last_print = "watching"
                pass

            chats = self.find_chat_references()
            print("chats: ", len(chats))
            for chat in chats:
                x, y, _, _ = cv2.boundingRect(chat)

                chat_id = self.extract_chat_id(chat_ref=(x, y))
                print("Chat id: ", chat_id)
                self.click_chat(chat_ref=(x, y), duration=1)


                if chat_id:
                    chat = self.chat_querys.get_chat_by_id_scraped(
                        id_scraped=chat_id)

                    if not chat:
                        self.chat_querys.create_chat(id_scraped=chat_id)

                # self.move_to_chat()
                self.take_screenshot()
                texts_locations = await self.review_chat()
                print("texts_locations: ", len(texts_locations))

                # ===========================================================================================
                # TODO Camturar textos de chats
                # for text_location in texts_locations:
                #     x_start, y_start, scroll_pos_start = text_location[0]
                #     x_end, y_end, scroll_pos_end = text_location[1]
                #     literal_text = self.get_text_by_text_location(x_start, y_start, x_end, y_end,
                #                                    scroll_pos_start, scroll_pos_end)
                #     print("================= Texto Extraido ================= \n \n", literal_text)
                #
                time.sleep(1)

            # if len(chats) == 0 and self.previous_screenshot is not None:
            #     img_handler = ImgHandler(image=self.current_screenshot)
            #     error = img_handler.similarity_by_mse(image=self.previous_screenshot)
            #
            #     if error > 0:
            #         text = self.extract_chat_text()
            #         print("================= Texto Extraido ================= \n \n", text)

            self.previous_screenshot = self.current_screenshot