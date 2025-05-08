from pynput.mouse import Listener as MouseListener
import threading


class MouseBlocker:
    def __init__(self, blocked=True):
        """
        Inicializa el bloqueador del mouse.

        :param blocked: Si es True, el mouse comienza bloqueado. Si es False, está desbloqueado.
        """
        self.blocked = blocked
        self.listener_thread = threading.Thread(target=self._start_listener, daemon=True)
        self.listener_thread.start()

        if blocked:
            print("[MouseBlocker] El mouse físico está BLOQUEADO")
        else:
            print("[MouseBlocker] El mouse físico está DESBLOQUEADO")

    def on_move(self, x, y):
        if self.blocked:
            print(f"[Bloqueado] Movimiento del mouse a ({x}, {y})")
            return False  # Bloquea el evento

    def on_click(self, x, y, button, pressed):
        if self.blocked:
            print(f"[Bloqueado] Clic del mouse en ({x}, {y})")
            return False  # Bloquea el evento

    def _start_listener(self):
        with MouseListener(on_move=self.on_move, on_click=self.on_click) as listener:
            listener.join()

    def block(self):
        """Activa el bloqueo del mouse físico"""
        self.blocked = True
        print("[MouseBlocker] El mouse físico está BLOQUEADO")

    def unblock(self):
        """Desactiva el bloqueo del mouse físico"""
        self.blocked = False
        print("[MouseBlocker] El mouse físico está DESBLOQUEADO")