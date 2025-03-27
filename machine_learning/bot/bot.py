import numpy as np
import pyautogui
import cv2
from img_handler import ImgHandler
from img_to_text import img_to_text
import time
from db.chat_querys import ChatQuerys
import pyperclip

class Bot:
    def __init__(self, name: str, target_name: str, target_templates_paths: list[str]) -> None:
        self.name = name
        self.target_name = target_name

        self.previous_screenshot = None
        self.chats_reference = None
        self.chat_area_reference = None
        self.current_chat_id = None
        self.current_screenshot = None
        self.last_circles_references_detected = None
        self.target_templates_paths = target_templates_paths
        self.scroll_reference = None # Cuanto se ha desplazado el scroll desde el fondo.
        # self.target_template = cv2.imread(self.target_template_path)
        self.chat_querys = ChatQuerys()


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


    # TODO: Agregar que encuentre los puentos dentro del contorno donde van los chats
    # para achicar el cerco y disminuir el error
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
        assert self.chat_area_reference is None, \
            "move_to_chat error: Chat area reference is None."

        pyautogui.moveTo(self.chat_area_reference[0],
                         self.chat_area_reference[1],
                         duration=0.3
                         )


    def scroll_chat_area(self, direction='up', scroll_move=100):
        pyautogui.moveTo(self.chats_reference[0],
                         self.chats_reference[1],
                         duration=1)

        self.scroll_reference = scroll_move

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
        is_overflow = img_handler.is_top_edge_irregular(contour=chat_contour)
        return is_overflow


    def is_contour_already_watched(self, contour) -> bool:
        img_handler = self.get_last_chat_id_image()
        contour_image = img_handler.contour_to_image(contour=contour)
        similarity_error = img_handler.similarity_by_mse(image=contour_image)

        if similarity_error < 0.1:
            return True
        return False


    def get_texts_did_not_watched_list(self, possible_text_contours):
        texts_did_not_watched = []
        has_more = False

        for contour in possible_text_contours[::-1]:
            # Comparar img_roi con la ultima referencia del texto visto por el current chat id
            is_watched = self.is_contour_already_watched(contour=contour)

            if not is_watched:
                x, y, w, h = cv2.boundingRect(contour)
                start_location = (x, y, self.scroll_reference)
                end_location = (x + w, y + h, self.scroll_reference)
                texts_did_not_watched.append([start_location, end_location])

            else:
                has_more = True
                break

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


    def review_chat(self, has_more: bool = True, texts: list = None) -> list[list[tuple[int, int, int]]]:
        """
        This function extracts the texts into chat contour as little contours.
        Each text is returned as a contour.

        :param has_more: Flag to indicate if there are more texts to extract
        :param texts: Accumulated list of text contours
        :return: List of text contours
        """
        if texts is None:
            texts = []

        if not has_more:
            return texts

        img_handler = ImgHandler(image=self.current_screenshot)
        chats_contour, chat_contour, possible_text_contours = img_handler.get_contours_by_edges()
        x, y, w, h = cv2.boundingRect(chat_contour)
        self.chat_area_reference = (x, y, w, h)

        has_more, texts_did_not_watched = self.get_texts_did_not_watched_list(
            possible_text_contours=possible_text_contours
        )

        if has_more:
            # Si no se encuentra el último texto visto
            is_overflow = self.is_there_text_overflow()

            if is_overflow:

                # Caso cuando hay texto desbordado (tratamiento diferente)
                result_image = self.repair_irregular_top_edge(
                    image=self.current_screenshot, contour=chat_contour)

                img_handler = ImgHandler(image=result_image)
                _, _, conours_found = img_handler.get_contours_by_edges()
                contour_overflow = conours_found[0]
                x, y, w, h = cv2.boundingRect(contour_overflow)
                x_contour_overflow_end = x + w
                y_contour_overflow_end = y + h

                while True:
                    self.scroll_chat_area(direction="up", scroll_move=1)
                    self.take_screenshot()
                    is_overflow = self.is_there_text_overflow()

                    if not is_overflow:
                        result_image = self.repair_irregular_top_edge(
                            image=self.current_screenshot, contour=chat_contour)

                        img_handler = ImgHandler(image=result_image)
                        _, _, conours_found = img_handler.get_contours_by_edges()
                        contour_overflow = conours_found[0]
                        x, y, w, h = cv2.boundingRect(contour_overflow)
                        x_contour_overflow_start = x
                        y_contour_overflow_start = y

                        texts.append([(x_contour_overflow_start, y_contour_overflow_start, self.scroll_reference),
                                      (x_contour_overflow_end, y_contour_overflow_end, self.scroll_reference)])
                        break

            else:
                # Caso normal: hacer scroll y continuar el proceso
                self.scroll_chat_area(direction="up",
                                      scroll_move=self.chat_area_reference[-1])

            # Después de hacer scroll (en cualquier caso), volvemos a llamar a la función
            return self.review_chat(
                has_more=has_more,
                texts=texts + texts_did_not_watched
            )

        return texts + texts_did_not_watched


    def send_image(self):
        pass


    def get_text_by_text_location(self, x_start, y_start, x_end,
                                  y_end, scroll_pos_start, scroll_pos_end) -> None:
        self.scroll_chat_area(
            direction="up" if scroll_pos_start > self.scroll_reference else "down",
            scroll_move=scroll_pos_start)
        pyautogui.moveTo(x=x_start, y=y_start, duration=0.3)

        pyautogui.mouseDown(button="left")
        self.scroll_chat_area(
            direction="down",
            scroll_move=scroll_pos_end)
        pyautogui.moveTo(x=x_end, y=y_end, duration=0.3)

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

                if chat_id:
                    self.chat_querys.create_chat(id_scraped=chat_id)

                self.move_to_chat()
                texts_locations = self.review_chat()

                # ===========================================================================================
                # TODO Camturar textos de chats
                for text_location in texts_locations:
                    x_start, y_start, scroll_pos_start = text_location[0]
                    x_end, y_end, scroll_pos_end = text_location[1]
                    literal_text = self.get_text_by_text_location(x_start, y_start, x_end, y_end,
                                                   scroll_pos_start, scroll_pos_end)
                    print("================= Texto Extraido ================= \n \n", literal_text)

                time.sleep(1)

            # if len(chats) == 0 and self.previous_screenshot is not None:
            #     img_handler = ImgHandler(image=self.current_screenshot)
            #     error = img_handler.similarity_by_mse(image=self.previous_screenshot)
            #
            #     if error > 0:
            #         text = self.extract_chat_text()
            #         print("================= Texto Extraido ================= \n \n", text)

            self.previous_screenshot = self.current_screenshot