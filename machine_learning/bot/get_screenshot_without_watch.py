import pygetwindow as gw
import mss
import mss.tools

# Obtener la ventana del navegador por título
window = gw.getWindowsWithTitle('Título de la ventana del navegador')[0]

# Coordenadas de la ventana
left, top, width, height = window.left, window.top, window.width, window.height

# Capturar la ventana usando MSS
with mss.mss() as sct:
    # Definir la región de captura
    monitor = {"top": top, "left": left, "width": width, "height": height}

    # Tomar la captura
    screenshot = sct.grab(monitor)

    # Guardar la captura como archivo (opcional)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="captura.png")

print("Captura tomada exitosamente.")