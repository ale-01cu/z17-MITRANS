import pygetwindow as gw
from pygetwindow import Win32Window

class WindowHandler:
    def __init__(self, title: str = '', is_active: bool = False):
        self.window = None
        self.title = title
        self.class_name = None
        self.process_name = None
        self.pid = None
        self.is_active = is_active


    def get_all_windows_titles(self) -> list[str]:
        return [window.title for window in gw.getAllWindows()]


    def get_window(self) -> Win32Window | None:
        windows = gw.getAllWindows()
        for window in windows:
            if self.title.lower() in window.title.lower():
                self.window = window
                return self.window
        return None


    def maximize_window(self) -> bool:
        if not self.is_active: return False
        self.get_window()
        if self.window:
            # Si no está maximizada, la maximizamos
            if not self.window.isMaximized:
                self.window.maximize()

            # Enfocamos/ponemos en primer plano la ventana
            self.window.activate()
            return True

        else:
            raise ValueError("No window found.")


    def minimize_window(self) -> None:
        self.get_window()
        if self.window:
            self.window.minimize()
        else:
            raise ValueError("No window found.")


    def find_and_maximize(self) -> bool:
        """
        Busca una ventana por su título y la maximiza si existe.

        :return: True si se encontró y maximizó la ventana, False en caso contrario.
        """
        if not self.is_active: return False
        windows = gw.getAllWindows()
        for window in windows:
            if self.title.lower() in window.title.lower():
                self.window = window
                self.window.maximize()
                return True  # Ventana encontrada y maximizada
        return False  # No se encontró ninguna ventana


    def is_window_maximized(self) -> bool:
        """
        Verifica si la ventana asociada está actualmente maximizada.

        :return: True si la ventana está maximizada, False en caso contrario o si no hay ventana.
        """
        if self.window:
            return self.window.isMaximized
        return False
