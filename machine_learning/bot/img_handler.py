import cv2
import numpy as np
import pytesseract
try:
    from skimage.metrics import structural_similarity as ssim
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("Advertencia: scikit-image no instalado. No se calculará SSIM.")
    print("Instala con: pip install scikit-image")

"""

!pip install pyenchant
!sudo apt install enchant-2
!sudo apt install hunspell-es
!pip install easyocr --quiet

"""


CONFIG = {
    # Movil
    'LIGHT_IMG_TEXT_BG_MOVIL': {
        'hex': '#f1f2f6',
        'tolerance-lower-b': 20,
        'tolerance-lower-g': 20,
        'tolerance-lower-r': 20,
        'tolerance-upper-b': 13,
        'tolerance-upper-g': 13,
        'tolerance-upper-r': 13,
    },
    'DARK_IMG_TEXT_BG_MOVIL': {
        'hex': '#333333',
        'tolerance-lower-b': 13,
        'tolerance-lower-g': 13,
        'tolerance-lower-r': 13,
        'tolerance-upper-b': 20,
        'tolerance-upper-g': 20,
        'tolerance-upper-r': 20,
    },
    # Desktop
    'DARK_IMG_TEXT_BG': {
        'hex': '#333333',
        'tolerance-lower-b': 13,
        'tolerance-lower-g': 13,
        'tolerance-lower-r': 13,
        'tolerance-upper-b': 20,
        'tolerance-upper-g': 20,
        'tolerance-upper-r': 20,
    },
    'LIGHT_IMG_TEXT_BG': {
        'hex': '#f0f0f0',
        'tolerance-lower-b': 20,
        'tolerance-lower-g': 20,
        'tolerance-lower-r': 20,
        'tolerance-upper-b': 13,
        'tolerance-upper-g': 13,
        'tolerance-upper-r': 13,
    },
}


class ImgHandler:
    def __init__(self, img_path: str = None, image = None):
        self.img_path = img_path
        self.img = image.copy() \
            if image is not None \
            else cv2.imread(self.img_path)
        self.color_hex = None
        self.color_rgb = None
        self.color_bgr = None
        self.lower_bound = None
        self.upper_bound = None
        self.mask = None
        self.result = None
        self.possible_usernames = []
        self.all_messages = []
        self.coherent_messages = []
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # self.reader = easyocr.Reader(['es'], gpu=True)

        if self.img is None:
            raise Exception("No se pudo cargar la imagen. Verifica la ruta.")


    def get_img(self):
        return self.img

    def get_shape(self):
        return self.img.shape

    # Convierte de hex a RGB
    def hex_to_rgb_color(self, hex_color):
        self.color_hex = hex_color
        self.color_rgb = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        self.color_bgr = self.color_rgb[::-1]
        return self.color_rgb


    def to_bgr_color(self, color: list):
        blue_bgr = np.uint8([[color]])  # Color en formato BGR (OpenCV usa BGR)
        return blue_bgr


    def from_bgr_to_hsv(self, bgr_color):
        hsv_color = cv2.cvtColor(bgr_color, cv2.COLOR_BGR2HSV)
        return hsv_color


    def to_hsv_image(self):
        hsv_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        return hsv_image


    def to_blurred_image(self, image, ksize: tuple, sigmaX: int):
        blurred_image = cv2.GaussianBlur(image, ksize, sigmaX)
        return blurred_image


    # Establece un rango de tolerancia para capturar variaciones del color
    def set_color_tolerance(self, tolerance_lower_b,
                            tolerance_lower_g, tolerance_lower_r,
                            tolerance_upper_b, tolerance_upper_g,
                            tolerance_upper_r
                            ):
        """
        Establece los límites inferior y superior para el rango de colores basado en las tolerancias proporcionadas.

        :param tolerance_lower_b: Tolerancia inferior para el canal azul (B).
        :param tolerance_lower_g: Tolerancia inferior para el canal verde (G).
        :param tolerance_lower_r: Tolerancia inferior para el canal rojo (R).
        :param tolerance_upper_b: Tolerancia superior para el canal azul (B).
        :param tolerance_upper_g: Tolerancia superior para el canal verde (G).
        :param tolerance_upper_r: Tolerancia superior para el canal rojo (R).
        :return: Tupla con los límites inferior y superior.
        """
        # Calcular los límites inferior y superior usando las tolerancias
        self.lower_bound = np.array([
            max(0, self.color_bgr[0] - tolerance_lower_b),
            max(0, self.color_bgr[1] - tolerance_lower_g),
            max(0, self.color_bgr[2] - tolerance_lower_r)
        ])

        self.upper_bound = np.array([
            min(255, self.color_bgr[0] + tolerance_upper_b),
            min(255, self.color_bgr[1] + tolerance_upper_g),
            min(255, self.color_bgr[2] + tolerance_upper_r)
        ])

        return self.lower_bound, self.upper_bound


    def create_mask(self, image=None, lower_bound=None, upper_bound=None):
        """
        Crea una máscara binaria para el color objetivo.

        :param image:
        :param lower_bound: Límite inferior del rango de color (opcional).
        :param upper_bound: Límite superior del rango de color (opcional).
        :return: Máscara binaria (imagen en escala de grises).
        """
        # Usar los valores de self si no se proporcionan parámetros
        if image is None:
            image = self.img
        if lower_bound is None:
            lower_bound = self.lower_bound
        if upper_bound is None:
            upper_bound = self.upper_bound

        # Verificar que los valores necesarios estén definidos
        if lower_bound is None or upper_bound is None:
            raise ValueError("Los límites inferior y superior deben estar definidos.")

        # Crear la máscara
        self.mask = cv2.inRange(image, lower_bound, upper_bound)
        return self.mask


    def create_result(self, mask = None):
        """
        Crea una imagen con la máscara y las regiones extraídas.

        :param mask: la máscara.
        :return: Imagen con la máscara y las regiones extraídas.
        """
        self.result = cv2.bitwise_and(self.img, self.img,
                                      mask=mask if mask else self.mask
                                      )
        return self.result


    # def is_text_coherent(self, text):
    #     """
    #     Comprueba si el texto es coherente.
    #
    #     :param text: Texto a comprobar.
    #     :return: True si el texto es coherente, False en caso contrario.
    #     """
    #     dictionary = enchant.Dict("es")  # Diccionario en español
    #     words = text.split()
    #     if len(words) < 5:
    #         return False
    #     valid_words = [word for word in words if dictionary.check(word)]
    #     return len(valid_words) / len(words) > 0.8  # Umbral de coherencia


    def extract_text(self, image = None):
        """
        Extrae el texto de la imagen.

        :return: Texto extraído de la imagen.
        """
        # show image
        if self.result is not None:
            image = self.result
        elif image is None:
            image = self.img

        custom_config = r'--oem 3 --psm 6 -l spa'
        text = pytesseract.image_to_string(image, config=custom_config)

        text = text.encode('utf-8').decode('utf-8').strip()
        return text

        # result = self.reader.readtext(
        #     self.result if not image else image, lang='spa')
        #
        # counter = 1
        #
        # for item in result:
        #     text = item[1]
        #     isCoherent = self.is_text_coherent(text)
        #
        #     if counter < 8 and isCoherent:
        #         self.possible_usernames.append(text)
        #         counter += 1
        #
        #     if isCoherent and len(text) > 20:
        #         self.coherent_messages.append(text)
        #
        #     self.all_messages.append(text)
        #
        # return {
        #     'possible_usernames': self.possible_usernames,
        #     'all_messages': self.all_messages,
        #     'coherent_messages': self.coherent_messages
        # }


    def save_results(self, output_path='result.png'):
        """
        Guarda la máscara y las regiones extraídas en archivos.

        :param output_path: Ruta donde se guardará el resultado.
        """
        cv2.imwrite(output_path, self.result)


    def is_dark_mode(self) -> bool:
        gray_image = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        average_brightness = np.mean(gray_image)
        threshold = 128  # Umbral típico para distinguir claro de oscuro

        if average_brightness < threshold:
            return True
        else:
            return False


    # Calcular el error cuadrático medio de las dos imagenes para saber su similitud
    def similarity_by_mse(self, image):
        image = cv2.resize(image, (self.img.shape[1], self.img.shape[0]))
        error = np.sum((image.astype("float") - self.img.astype("float")) ** 2)
        error /= float(image.shape[0] * image.shape[1])
        return error



    def detect_circles(self, image, dp=1, minDist=10, param1=50,
                       param2=20, minRadius=5, maxRadius=7 ):

        circles = cv2.HoughCircles(
            image,
            cv2.HOUGH_GRADIENT,
            dp=dp,
            minDist=minDist,  # Distancia mínima entre centros de círculos
            param1=param1,  # Sensibilidad del detector de bordes
            param2=param2,  # Umbral para detectar círculos (reduce para círculos pequeños)
            minRadius=minRadius,  # Radio mínimo del círculo (ajustado para círculos pequeños)
            maxRadius=maxRadius  # Radio máximo del círculo (ajustado para círculos pequeños)
        )

        return circles


    def find_contours(self, image):
        contours, _ = cv2.findContours(image,
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_NONE
                                       )

        return contours


    def save_image(self):
        cv2.imwrite("image_test.png", self.img)


    def get_edged(self, image = None):
        edged = cv2.Canny(image if image is not None else self.img, 30, 200)
        return edged


    def get_contours_by_edges(self, image = None):
        color_hex = '#f0f0f0'
        color_rgb = tuple(int(color_hex[i:i + 2], 16) for i in (1, 3, 5))  # Convierte de hex a RGB
        color_bgr = color_rgb[::-1]  # Convierte de RGB a BGR

        # Establece un rango de tolerancia para capturar variaciones del color
        lower_bound = np.array([max(0, color_bgr[0] - 20), max(0, color_bgr[1] - 20), max(0, color_bgr[2] - 20)])
        upper_bound = np.array([min(255, color_bgr[0] + 13), min(255, color_bgr[1] + 13), min(255, color_bgr[2] + 13)])

        # Paso 3: Crear una máscara para el color objetivo
        mask = cv2.inRange(image if image is not None else self.img, lower_bound, upper_bound)

        edged = self.get_edged(mask)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours_found = []
        chats_contour = None
        margin = 10
        possible_chat_contours = []
        chat_contour = None
        possible_text_contours = []

        # Filter small contours leaving only large contours | Tested
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)

            if chats_contour is None:
                chats_contour = contour

            x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

            if chats_contour is not None and x == 0 and y_chats > y and h_chats < h:
                chats_contour = contour

            if x > 50 and h > 20:
                contours_found.append(contour)

        # Find possible chat contour nearby | Tested
        for contour in contours_found:
            x, y, w, h = cv2.boundingRect(contour)
            x_chats, y_chats, w_chats, h_chats = cv2.boundingRect(chats_contour)

            if x < 50 or h < 20:
                continue

            if abs(x - (x_chats + w_chats)) < margin:
                print("pase")
                possible_chat_contours.append(contour)

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

        for contour in contours_found:
            x, y, w, h = cv2.boundingRect(contour)

            # Filtro de tamaño (ajusta según necesidad)
            if (70 < w < 600) and (h < 50):
                # Verifica si está DENTRO del chat_contour
                if (x_chat <= x) and (x + w <= x_chat + w_chat) and (y_chat <= y) and (y + h <= y_chat + h_chat):
                    possible_text_contours.append(contour)


        return chats_contour, chat_contour, possible_text_contours



    def contour_to_image(self, contour, image = None):
        x, y, w, h = cv2.boundingRect(contour)
        if image is not None:
            img_roi = image[y:y + h, x:x + w]
        else:
            img_roi = self.img[y:y + h, x:x + w]

        return img_roi


    def is_top_edge_irregular(self, contour, threshold=1, edge_margin_left=5,
                              edge_margin_right=5, analyze_percent=100):
        """
        Determina si el borde superior de un contorno tiene alguna irregularidad en un porcentaje específico del mismo.

        Args:
            contour (numpy.ndarray): El contorno en formato de un array de puntos.
            threshold (int): Umbral para considerar una diferencia significativa en 'y'.
            edge_margin_left (int): Margen en píxeles para excluir el borde izquierdo.
            edge_margin_right (int): Margen en píxeles para excluir el borde derecho.
            analyze_percent (int): Porcentaje del borde superior a analizar (0-100).
                                  Ejemplo: 25 analiza solo el primer 25% del borde.

        Returns:
            bool: True si el borde superior tiene una irregularidad ("baja") en el área analizada,
                  False si está completamente recto en esa sección.
        """
        # Validar el porcentaje de análisis
        if contour is None:
            raise ValueError("No se proporcionó el contorno.")

        analyze_percent = max(0, min(100, analyze_percent))

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
        x_coords = [x for x, y in sorted_top_edge]
        y_coords = [y for x, y in sorted_top_edge]

        # Excluir los bordes laterales según los márgenes especificados
        if len(x_coords) <= (edge_margin_left + edge_margin_right):
            return False  # No hay suficientes puntos para analizar después de excluir los bordes

        start_index = edge_margin_left
        end_index = len(x_coords) - edge_margin_right

        # Calcular el punto final basado en el porcentaje a analizar
        if analyze_percent < 100:
            total_central_points = end_index - start_index
            analyze_points = int(total_central_points * analyze_percent / 100)
            end_index = start_index + analyze_points

        # Filtrar las coordenadas dentro del rango especificado
        central_x_coords = x_coords[start_index:end_index]
        central_y_coords = y_coords[start_index:end_index]

        # Si no hay suficientes puntos después del filtrado
        if len(central_x_coords) < 2:
            return False

        # Calcular las diferencias consecutivas en 'y' para detectar irregularidades
        y_diffs = np.diff(central_y_coords)

        # Detectar si alguna diferencia es positiva (indica que el borde "baja")
        is_incomplete = any(diff > threshold for diff in y_diffs)

        return is_incomplete


    def is_bottom_edge_irregular(self, contour, threshold=1, edge_margin_left=5,
                                 edge_margin_right=5, analyze_percent=100):
        """
        Determina si el borde inferior de un contorno tiene alguna irregularidad ("subida")
        en un porcentaje específico del mismo.

        Args:
            contour (numpy.ndarray): El contorno en formato de un array de puntos.
            threshold (int): Umbral para considerar una diferencia significativa en 'y'.
                             Una diferencia negativa (menor que -threshold) indica una "subida".
            edge_margin_left (int): Margen en píxeles para excluir el borde izquierdo.
            edge_margin_right (int): Margen en píxeles para excluir el borde derecho.
            analyze_percent (int): Porcentaje del borde inferior a analizar (0-100).
                                  Ejemplo: 25 analiza solo el primer 25% del borde (desde la izquierda).

        Returns:
            bool: True si el borde inferior tiene una irregularidad ("sube") en el área analizada,
                  False si está completamente recto o solo "baja" en esa sección.
        """
        # Validar el porcentaje de análisis
        analyze_percent = max(0, min(100, analyze_percent))

        # Extraer los puntos del contorno
        points = contour[:, 0]  # Los puntos están almacenados como un array de shape (N, 1, 2)

        # Crear un diccionario para almacenar el valor máximo de 'y' para cada 'x'
        bottom_edge_points = {}
        for x, y in points:
            # Buscamos el punto más bajo (mayor 'y') para cada columna 'x'
            if x not in bottom_edge_points or y > bottom_edge_points[x]:
                bottom_edge_points[x] = y

        # Convertir el diccionario en una lista ordenada por 'x'
        sorted_bottom_edge = sorted(bottom_edge_points.items(), key=lambda item: item[0])

        # Si no hay puntos en el borde inferior extraído, no hay irregularidad
        if not sorted_bottom_edge:
            return False

        # Extraer las coordenadas x e y del borde inferior
        x_coords = [x for x, y in sorted_bottom_edge]
        y_coords = [y for x, y in sorted_bottom_edge]

        # Excluir los bordes laterales según los márgenes especificados
        if len(x_coords) <= (edge_margin_left + edge_margin_right):
            return False  # No hay suficientes puntos para analizar después de excluir los bordes

        start_index = edge_margin_left
        end_index = len(x_coords) - edge_margin_right

        # Calcular el punto final basado en el porcentaje a analizar
        # El análisis se hace desde la izquierda (índice menor) hacia la derecha
        if analyze_percent < 100:
            total_central_points = end_index - start_index
            analyze_points = int(total_central_points * analyze_percent / 100)
            # Asegurarse de que analyze_points sea al menos 1 si total_central_points > 0
            analyze_points = max(1, analyze_points) if total_central_points > 0 else 0
            end_index = start_index + analyze_points
            # Asegurar que end_index no exceda el límite original
            end_index = min(end_index, len(x_coords) - edge_margin_right)

        # Filtrar las coordenadas dentro del rango especificado
        central_x_coords = x_coords[start_index:end_index]
        central_y_coords = y_coords[start_index:end_index]

        # Si no hay suficientes puntos después del filtrado para calcular diferencias
        if len(central_x_coords) < 2:
            return False

        # Calcular las diferencias consecutivas en 'y' para detectar irregularidades
        y_diffs = np.diff(central_y_coords)

        # Detectar si alguna diferencia es significativamente negativa (indica que el borde "sube")
        # En coordenadas de imagen, un valor 'y' menor significa estar más arriba.
        # Por lo tanto, una diferencia negativa (y_actual - y_anterior < 0) significa que el borde subió.
        is_irregular_upward = any(diff < -threshold for diff in y_diffs)

        return is_irregular_upward


    def create_mask_to_large_contours(self, image=None):
        color_hex = '#f0f0f0'
        color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (1, 3, 5))  # Convierte de hex a RGB
        color_bgr = color_rgb[::-1]  # Convierte de RGB a BGR

        # Establece un rango de tolerancia para capturar variaciones del color
        lower_bound = np.array([max(0, color_bgr[0]-20), max(0, color_bgr[1]-20), max(0, color_bgr[2]-20)])
        upper_bound = np.array([min(255, color_bgr[0]+13), min(255, color_bgr[1]+13), min(255, color_bgr[2]+13)])

        # Paso 3: Crear una máscara para el color objetivo
        mask = cv2.inRange(image if image is not None else self.img, lower_bound, upper_bound)

        return mask


    def find_contours_by_large_contours_mask(self, image=None):
        mask = self.create_mask_to_large_contours(image=image if image is not None else self.img)
        edged = self.get_edged(mask)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        return contours


    # Detecta si hay algun borde horizontal con una discontinuidad
    def has_irregular_horizontal_edge(
            self,
            contour,
            y_threshold=5,
            x_threshold=5,
            slope_threshold=2,
            corner_margin=5
    ):
        """
        Detecta irregularidades en bordes horizontales, excluyendo esquinas redondeadas.

        Args:
            contour (numpy.ndarray): Contorno en formato de array de puntos.
            y_threshold (int): Umbral para detectar desviaciones hacia abajo.
            x_threshold (int): Umbral para detectar discontinuidades.
            slope_threshold (int): Variación máxima en 'y' entre puntos consecutivos.
            corner_margin (int): Píxeles a excluir en los extremos de cada borde horizontal.

        Returns:
            bool: True si hay irregularidades en bordes horizontales.
        """
        if len(contour) < 2:
            return False

        current_edge = []
        start_y = None

        for point in contour[:, 0]:
            x, y = point

            if not current_edge:
                current_edge.append((x, y))
                start_y = y
            else:
                delta_consecutive = abs(y - current_edge[-1][1])
                delta_cumulative = abs(y - start_y)

                # Continuar el borde si cumple ambas condiciones
                if delta_consecutive <= slope_threshold and delta_cumulative <= y_threshold * 2:
                    current_edge.append((x, y))
                else:
                    if len(current_edge) >= 2:
                        if self.check_irregularities(current_edge, y_threshold, x_threshold, corner_margin):
                            return True
                    # Reiniciar el borde
                    current_edge = [(x, y)]
                    start_y = y

        # Verificar el último borde
        if len(current_edge) >= 2:
            if self.check_irregularities(current_edge, y_threshold, x_threshold, corner_margin):
                return True

        return False


    def check_irregularities(self, edge, y_threshold, x_threshold, corner_margin):
        """Verifica irregularidades excluyendo las esquinas."""
        if len(edge) <= 2 * corner_margin:
            return False  # Borde demasiado corto después de excluir esquinas

        # Excluir margen de esquinas
        trimmed_edge = edge[corner_margin:-corner_margin]
        if not trimmed_edge:
            return False

        baseline_y = trimmed_edge[0][1]  # Referencia desde la zona central

        # 1. Detectar desviación hacia abajo (ahora incluye igualdad)
        for x, y in trimmed_edge:
            if y - baseline_y >= y_threshold:  # Cambiado de > a >=
                return True

        # 2. Detectar discontinuidades
        for i in range(len(trimmed_edge) - 1):
            x1, y1 = trimmed_edge[i]
            x2, y2 = trimmed_edge[i + 1]
            if abs(x2 - x1) > x_threshold:
                return True

        return False


    def compare_messenger_images_with_contours(self,
                                                img_path1=None, img_data1=None,
                                                img_path2=None, img_data2=None,
                                                ignored_contours=[], threshold=10
                                               ):
        """
        Compara dos imágenes ignorando regiones definidas por contornos de OpenCV.

        Args:
            img_path1 (str): Ruta a la primera imagen.
            img_path2 (str): Ruta a la segunda imagen.
            ignored_contours (list): Una lista de contornos de OpenCV. Cada contorno
                                     es un array NumPy de puntos (e.g., [[x1, y1], [x2, y2],...]).
                                     Las áreas dentro de estos contornos serán ignoradas.
            threshold (int): Umbral de diferencia de píxeles permitido en las áreas
                             no ignoradas. 0 significa igualdad exacta.

        Returns:
            bool: True si las imágenes son consideradas iguales (ignorando las regiones),
                  False en caso contrario.
            numpy.ndarray: La imagen de diferencia (opcional, para visualización).
            float: El puntaje de similitud SSIM (si scikit-image está disponible),
                   de lo contrario 0.0.
        """
        img1 = None
        img2 = None

        # --- Carga/Asignación de Imagen 1 ---
        if img_data1 is not None:
            if isinstance(img_data1, np.ndarray):
                # Usar datos directamente. Copiar para evitar modificar el original.
                img1 = img_data1.copy()
                # print("Usando datos proporcionados para Imagen 1.")
            else:
                print("Error: img_data1 proporcionado pero no es un array NumPy válido.")
                return False, None, 0.0
        elif img_path1 is not None:
            img1 = cv2.imread(img_path1)
            if img1 is None:
                print(f"Error: No se pudo cargar la imagen desde la ruta {img_path1}")
                return False, None, 0.0
            print(f"Imagen 1 cargada desde {img_path1}.")
        else:
            # Error: no se proporcionó ni ruta ni datos para la imagen 1
            img1 = self.img.copy()
            if isinstance(img1, np.ndarray):
                # Usar datos directamente. Copiar para evitar modificar el original.
                img1 = img1.copy()
                # print("Usando datos proporcionados para Imagen 1.")
            else:
                print("Error: img1 proporcionado pero no es un array NumPy válido.")
                return False, None, 0.0

        # --- Carga/Asignación de Imagen 2 ---
        if img_data2 is not None:
            if isinstance(img_data2, np.ndarray):
                img2 = img_data2.copy()
#                 print("Usando datos proporcionados para Imagen 2.")
            else:
                print("Error: img_data2 proporcionado pero no es un array NumPy válido.")
                # Podríamos querer liberar img1 si fue cargado, pero Python GC lo hará
                return False, None, 0.0
        elif img_path2 is not None:
            img2 = cv2.imread(img_path2)
            if img2 is None:
                print(f"Error: No se pudo cargar la imagen desde la ruta {img_path2}")
                return False, None, 0.0
            print(f"Imagen 2 cargada desde {img_path2}.")
        else:
            # Error: no se proporcionó ni ruta ni datos para la imagen 2
            raise ValueError("Debe proporcionar 'img_path2' o 'img_data2'.")

        # Verificar si tienen las mismas dimensiones
        if img1.shape != img2.shape:
            print("Img 1 shape: ", img1.shape)
            print("Img 2 shape: ", img2.shape)
            print("Error: Las imágenes tienen dimensiones diferentes.")
            return False, None, 0.0

        height, width, _ = img1.shape

        # --- Crear la Máscara ---
        # Empezamos con una máscara blanca (todo se compara por defecto)
        mask = np.full((height, width), 255, dtype=np.uint8)

        # Dibujar los contornos a ignorar sobre la máscara, RELLENÁNDOLOS de negro (0)
        # cv2.drawContours espera una lista de contornos.
        # El índice -1 dibuja todos los contornos de la lista.
        # El color 0 es negro.
        # cv2.FILLED (-1) rellena el interior de los contornos.
        # if ignored_contours:  # Solo dibujar si la lista no está vacía
        #     cv2.drawContours(mask, ignored_contours, -1, color=0, thickness=cv2.FILLED)

        # --- Aplicar la Máscara a ambas imágenes ---
        masked_img1 = cv2.bitwise_and(img1, img1, mask=mask)
        masked_img2 = cv2.bitwise_and(img2, img2, mask=mask)

        # --- Comparación 1: Diferencia Absoluta ---
        diff = cv2.absdiff(masked_img1, masked_img2)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        non_zero_count = cv2.countNonZero(gray_diff)
        are_equal_diff = non_zero_count <= threshold

        # --- Comparación 2: SSIM (Índice de Similitud Estructural) ---
        score = 0.0
        are_equal_ssim = False  # Valor por defecto si SSIM no se calcula
        if SKIMAGE_AVAILABLE:
            gray_masked1 = cv2.cvtColor(masked_img1, cv2.COLOR_BGR2GRAY)
            gray_masked2 = cv2.cvtColor(masked_img2, cv2.COLOR_BGR2GRAY)
            try:
                # Calcular SSIM en las imágenes enmascaradas (las áreas ignoradas son negras)
                score, _ = ssim(gray_masked1, gray_masked2, full=True,
                                data_range=gray_masked1.max() - gray_masked1.min())

                ssim_threshold = 0.98  # Umbral de ejemplo para SSIM
                are_equal_ssim = score >= ssim_threshold
            except ValueError as e:
                # Puede ocurrir si una imagen es completamente negra después de enmascarar
                # o si hay muy poca varianza.
                print(f"Advertencia al calcular SSIM: {e}")
                # En este caso, podríamos depender solo de la diferencia absoluta.
                score = 0.0  # O algún otro valor indicativo
                are_equal_ssim = False  # O basarlo en are_equal_diff si score es 0

        # Devolver resultado
        # print(f"Píxeles diferentes (ignorando contornos): {non_zero_count}")
        # if SKIMAGE_AVAILABLE:
        #     print(f"Puntaje SSIM (en áreas comparadas): {score:.4f}")

        # Puedes decidir la lógica final para devolver True/False
        # Por ejemplo, podrías requerir que ambas métricas pasen, o solo una.
        # Aquí usamos la diferencia absoluta como principal criterio.
        final_result = are_equal_diff

        return final_result, diff, score





