import pygetwindow as gw
from pygetwindow import Win32Window

class WindowHandler:
    def __init__(self, title: str = ''):
        self.window = None
        self.title = title
        self.class_name = None
        self.process_name = None
        self.pid = None

    def get_all_windows_titles(self) -> list[str]:
        return [window.title for window in gw.getAllWindows()]

    def get_window(self) -> Win32Window | None:
        windows = gw.getAllWindows()
        for window in windows:
            if self.title.lower() in window.title.lower():
                self.window = window
                return self.window
        return None

    def maximize_window(self) -> None:
        if self.window:
            self.window.maximize()
        else:
            raise ValueError("No window found. Call get_window() first.")
