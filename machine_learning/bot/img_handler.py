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

class ImgHandler:
    def __init__(self, img_path, image):
        self.img_path = img_path
        self.img = image if image is not None else cv2.imread(self.img_path)
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


    # Convierte de hex a RGB
    def hex_to_rgb_color(self, hex_color):
        self.color_hex = hex_color
        self.color_rgb = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        self.color_bgr = self.color_rgb[::-1]
        return self.color_rgb


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


    def create_mask(self):
        """
        Crea una máscara binaria para el color objetivo.

        :return: Máscara binaria (imagen en escala de grises).
        """
        self.mask = cv2.inRange(self.img, self.lower_bound, self.upper_bound)
        return self.mask


    def create_result(self, mask = None):
        """
        Crea una imagen con la máscara y las regiones extraídas.

        :param mask: la máscara.
        :return: Imagen con la máscara y las regiones extraídas.
        """
        self.result = cv2.bitwise_and(self.img, self.img, mask=mask if mask else self.mask)
        return self.result


    # def is_text_coherent(self, text):
    #     """
    #     Comprueba si el texto es coherente.

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
        
        text = pytesseract.image_to_string(self.result if not image else image)
        return text
        # result = self.reader.readtext(
        #     self.result if not image else image, lang='spa')

        # counter = 1

        # for item in result:
        #     text = item[1]
        #     isCoherent = self.is_text_coherent(text)

        #     if counter < 8 and isCoherent:
        #         self.possible_usernames.append(text)
        #         counter += 1

        #     if isCoherent and len(text) > 20:
        #         self.coherent_messages.append(text)

        #     self.all_messages.append(text)

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

