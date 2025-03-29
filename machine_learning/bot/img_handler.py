import cv2
import numpy as np
# import enchant
# import easyocr
import pytesseract

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
        self.img = image \
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

        text = pytesseract.image_to_string(image, lang='spa')
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



    def is_top_edge_irregular(contour, threshold=1, edge_margin=5):
        """
        Determina si el borde superior de un contorno tiene alguna irregularidad,
        específicamente si "baja" en algún punto (excepto en los bordes).

        Args:
            contour (numpy.ndarray): El contorno en formato de un array de puntos.
            threshold (int): Umbral para considerar una diferencia significativa en 'y'.
            edge_margin (int): Margen en píxeles para excluir los bordes izquierdo y derecho.

        Returns:
            bool: True si el borde superior tiene una irregularidad ("baja"), False si está completamente recto.
        """
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

        # Excluir los bordes laterales según el margen especificado
        if len(x_coords) <= 2 * edge_margin:
            return False  # No hay suficientes puntos para analizar después de excluir los bordes

        start_index = edge_margin
        end_index = len(x_coords) - edge_margin

        # Filtrar las coordenadas dentro del rango central
        central_x_coords = x_coords[start_index:end_index]
        central_y_coords = y_coords[start_index:end_index]

        # Calcular las diferencias consecutivas en 'y' para detectar irregularidades
        y_diffs = np.diff(central_y_coords)

        # Detectar si alguna diferencia es positiva (indica que el borde "baja")
        is_incomplete = any(diff > threshold for diff in y_diffs)

        return is_incomplete


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



