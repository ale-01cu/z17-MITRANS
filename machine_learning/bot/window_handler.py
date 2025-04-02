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
        titles = gw.getAllWindows()
        return titles


    def get_window(self) -> Win32Window | None:
        titles = self.get_all_windows_titles()

        for title in titles:
            if self.title.lower() in title.lower():
                windwos_found = gw.getWindowsWithTitle(title)
                self.window = windwos_found[0] if len(windwos_found) > 0 else None
                return self.window

        return None


    def maximize_window(self) -> None:
        self.window.maximize()