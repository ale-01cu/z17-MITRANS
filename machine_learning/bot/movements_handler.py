import pyautogui
import random
import time
import math
from typing import List, Tuple

class MovementsHandler:

    def __init__(self):
        pass

    def human_like_mouse_move(self, start, end, duration=None):
        """
        Mueve el mouse de forma rápida pero natural, con trayectoria aleatoria.
        """
        x1, y1 = start
        x2, y2 = end

        # Validaciones
        if duration is not None and duration <= 0:
            raise ValueError("La duración debe ser mayor que 0.")

        # Ajustamos la duración total a un rango más rápido
        if duration is None:
            duration = random.uniform(0.15, 0.6)  # Movimiento muy rápido pero natural

        # Seleccionar tipo de trayectoria aleatoriamente
        path_type = random.choice([
            "bezier_cubic",
            "bezier_random_control",
            "waypoints",
            "straight_with_noise"
        ])

        # Generar camino según el tipo seleccionado
        if path_type == "bezier_cubic":
            path = self._generate_bezier_cubic_path(start, end)
        elif path_type == "bezier_random_control":
            path = self._generate_bezier_random_control_path(start, end)
        elif path_type == "waypoints":
            path = self._generate_waypoints_path(start, end)
        else:
            path = self._generate_straight_with_noise_path(start, end)

        # Moverse a lo largo del camino generado
        self._move_along_path_fast(path, duration)


    def _generate_bezier_cubic_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Genera una curva de Bézier cúbica entre dos puntos"""
        x1, y1 = start
        x2, y2 = end

        # Puntos de control fijos para una curva cúbica natural
        control1 = (x1 + (x2 - x1) * 0.2, y1 + (y2 - y1) * 0.8)
        control2 = (x1 + (x2 - x1) * 0.8, y1 + (y2 - y1) * 0.2)

        return self._bezier_curve([start, control1, control2, end], segments=20)


    def _generate_bezier_random_control_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[
        Tuple[int, int]]:
        """Genera una curva de Bézier con puntos de control aleatorios"""
        x1, y1 = start
        x2, y2 = end

        # Generar puntos de control aleatorios dentro de límites razonables
        dx = x2 - x1
        dy = y2 - y1

        control1 = (
            x1 + random.uniform(0.2, 0.4) * dx + random.uniform(-50, 50),
            y1 + random.uniform(0.2, 0.4) * dy + random.uniform(-50, 50)
        )
        control2 = (
            x1 + random.uniform(0.6, 0.8) * dx + random.uniform(-50, 50),
            y1 + random.uniform(0.6, 0.8) * dy + random.uniform(-50, 50)
        )

        return self._bezier_curve([start, control1, control2, end], segments=20)


    def _generate_waypoints_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Genera un camino con puntos intermedios aleatorios"""
        x1, y1 = start
        x2, y2 = end

        # Distancia entre puntos
        distance = math.hypot(x2 - x1, y2 - y1)
        num_waypoints = max(2, min(int(distance / 150), 5))  # 2-5 waypoints según la distancia

        # Generar waypoints aleatorios
        waypoints = [start]
        for _ in range(num_waypoints - 1):
            prev_x, prev_y = waypoints[-1]
            remaining_x = x2 - prev_x
            remaining_y = y2 - prev_y

            # Avanzar un porcentaje aleatorio hacia el destino
            progress = random.uniform(0.2, 0.5)
            next_x = prev_x + remaining_x * progress + random.uniform(-30, 30)
            next_y = prev_y + remaining_y * progress + random.uniform(-30, 30)

            waypoints.append((next_x, next_y))

        waypoints.append(end)

        # Interpolar entre waypoints con Bézier cuadrática
        path = []
        for i in range(len(waypoints) - 1):
            segment = self._bezier_curve(
                [waypoints[i], (
                    (waypoints[i][0] + waypoints[i + 1][0]) / 2 + random.uniform(-20, 20),
                    (waypoints[i][1] + waypoints[i + 1][1]) / 2 + random.uniform(-20, 20)
                ), waypoints[i + 1]],
                segments=10
            )
            path.extend(segment)

        return path


    def _generate_straight_with_noise_path(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Genera un camino recto con ruido aleatorio"""
        x1, y1 = start
        x2, y2 = end

        steps = 20
        path = []

        dx = x2 - x1
        dy = y2 - y1

        for i in range(steps + 1):
            t = i / steps
            x = x1 + dx * t
            y = y1 + dy * t

            # Añadir ruido solo en algunos puntos
            if i % 4 == 0 and i != 0 and i != steps:
                x += random.uniform(-10, 10)
                y += random.uniform(-10, 10)

            path.append((x, y))

        return path


    def _bezier_curve(self, control_points: List[Tuple[int, int]], segments: int) -> List[Tuple[int, int]]:
        """Calcula puntos en una curva de Bézier de cualquier grado"""

        def bezier_point(t, points):
            n = len(points) - 1
            x = y = 0
            for i, (px, py) in enumerate(points):
                bernstein = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
                x += px * bernstein
                y += py * bernstein
            return (x, y)

        return [bezier_point(i / segments, control_points) for i in range(segments + 1)]


    def _move_along_path(self, path: List[Tuple[int, int]], duration: float):
        """Mueve el cursor a lo largo de un camino con comportamiento humano"""
        total_points = len(path)
        start_time = time.time()

        # Determinar si hay pausa durante el movimiento
        has_pause = random.random() < 0.3  # 30% de chance de pausa
        pause_point = random.randint(total_points // 4, total_points * 3 // 4)

        # Velocidad variable
        speed_factor = random.uniform(0.8, 1.2)

        # Aceleración natural
        def ease(t):
            return t ** 1.5  # Aceleración inicial

        for i, (x, y) in enumerate(path):
            # Verificar si es momento de pausar
            if has_pause and i == pause_point:
                pause_duration = random.uniform(0.2, 0.5)
                print(f"Pausa de {pause_duration:.2f}s durante movimiento")
                time.sleep(pause_duration)

            # Calcular tiempo progresivo con aceleración
            elapsed = time.time() - start_time
            t = min(elapsed / duration, 1.0)

            # Mover solo si el tiempo ha avanzado lo suficiente
            if i / total_points <= t:
                pyautogui.moveTo(x, y)
                # Dormir un poco para controlar la velocidad
                sleep_time = random.uniform(0.008, 0.015) / speed_factor
                time.sleep(sleep_time)
            else:
                # Saltar este punto y esperar un poco
                time.sleep(0.005)

        # Asegurar posición final exacta
        pyautogui.moveTo(path[-1][0], path[-1][1])


    def _move_along_path_fast(self, path: List[Tuple[int, int]], duration: float):
        """Mueve el cursor rápidamente pero con comportamiento humano"""
        total_points = len(path)
        start_time = time.time()

        # Aceleración más pronunciada
        def ease(t):
            return t ** 2.5  # Aceleración más fuerte al inicio

        # Probabilidad de pausa reducida
        has_pause = random.random() < 0.15  # Solo 15% de chance de pausa
        pause_point = random.randint(total_points // 4, total_points * 3 // 4)

        # Velocidad variable pero más rápida
        speed_factor = random.uniform(1.0, 1.5)  # Más rápido por defecto

        for i, (x, y) in enumerate(path):
            elapsed = time.time() - start_time
            t = min(elapsed / duration, 1.0)

            # Si es momento de pausar
            if has_pause and i == pause_point:
                pause_duration = random.uniform(0.05, 0.15)
                time.sleep(pause_duration)

            # Mover solo si el tiempo ha avanzado lo suficiente
            if i / total_points <= t:
                pyautogui.moveTo(x, y)
                # Dormir menos para aumentar velocidad
                sleep_time = random.uniform(0.002, 0.005) / speed_factor
                time.sleep(sleep_time)
            else:
                time.sleep(0.002)  # Saltar y esperar menos

        # Asegurar posición final exacta
        pyautogui.moveTo(path[-1][0], path[-1][1])


    def human_like_scroll(self, scroll_amount, steps=None, base_delay=0.05):
        """
        Simula un scroll vertical de manera similar a como lo haría un humano.

        :param scroll_amount: Unidades de scroll (positivo = hacia arriba, negativo = hacia abajo)
        :param steps: Número de pasos en los que dividir el scroll
        :param base_delay: Retraso base entre scrolls (en segundos)
        """
        total_scroll = scroll_amount
        direction = 1 if total_scroll > 0 else -1  # 1 para arriba, -1 para abajo

        if steps is None:
            steps = random.randint(5, 10)  # Cantidad de movimientos discretos

        remaining = abs(total_scroll)

        for i in range(steps):
            # Determinamos cuánto scroll hacer en este paso
            if i == steps - 1:
                scroll_step = remaining * direction  # Último paso consume lo restante
            else:
                # Paso aleatorio proporcional al restante
                step_size = random.uniform(0.1, 0.4) * remaining
                scroll_step = int(step_size) * direction
                remaining -= abs(scroll_step)

            # Aplicamos el scroll
            pyautogui.scroll(scroll_step)

            # Añadimos una pausa aleatoria
            delay = base_delay + random.uniform(0.01, 0.05)
            time.sleep(delay)

            # 15% de probabilidad de vacilar (hacer scroll en dirección contraria brevemente)
            if random.random() < 0.15 and i != steps - 1:  # No en último paso
                correction = random.randint(5, 20) * (-direction)
                pyautogui.scroll(correction)
                time.sleep(random.uniform(0.05, 0.15))
