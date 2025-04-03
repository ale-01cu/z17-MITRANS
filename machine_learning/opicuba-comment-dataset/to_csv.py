# Transport related questions
transport = [
    {"comment": "¿Cuál es el horario de salida de los ómnibus desde La Habana a Santiago de Cuba este fin de semana?", "label": "pregunta"},
    {"comment": "¿Por qué el tren de Matanzas a Varadero no está funcionando hoy?", "label": "pregunta"},
    {"comment": "¿Hay alguna ruta alternativa para llegar a Pinar del Río desde Artemisa?", "label": "pregunta"},
    {"comment": "¿Los taxis colectivos aceptan pago en MLC o solo en CUP?", "label": "pregunta"},
    {"comment": "¿Dónde puedo reclamar si el ómnibus no pasó a su hora programada?", "label": "pregunta"}
]

# Electric service related questions
electric = [
    {"comment": "¿A qué horas habrá corte de luz en Centro Habana hoy?", "label": "pregunta"},
    {"comment": "¿Cómo puedo reportar un poste de luz que está a punto de caerse en mi barrio?", "label": "pregunta"},
    {"comment": "¿Por qué la factura de este mes viene más alta si consumí menos kWh?", "label": "pregunta"},
    {"comment": "¿Qué debo hacer si mi medidor eléctrico no funciona correctamente?", "label": "pregunta"},
    {"comment": "¿Hay algún plan para mejorar el suministro eléctrico en mi zona?", "label": "pregunta"}
]

# Telecommunications related questions
telecom = [
    {"comment": "¿Cuándo llegará el servicio de Internet a mi casa en Güira de Melena?", "label": "pregunta"},
    {"comment": "¿Por qué no puedo recargar saldo en mi línea Nauta desde la aplicación?", "label": "pregunta"},
    {"comment": "¿Cómo activo el paquete de datos ilimitados de 1 día?", "label": "pregunta"},
    {"comment": "¿Dónde puedo comprar una tarjeta SIM en La Habana Vieja?", "label": "pregunta"},
    {"comment": "¿Por qué mi llamada internacional no se conecta aunque tengo saldo?", "label": "pregunta"}
]

# Banking related questions
bank = [
    {"comment": "¿Cuál es el límite de retiro diario en cajeros automáticos?", "label": "pregunta"},
    {"comment": "¿Cómo puedo activar mi tarjeta magnética nueva?", "label": "pregunta"},
    {"comment": "¿Por qué no me aparece el depósito que me hicieron en mi cuenta?", "label": "pregunta"},
    {"comment": "¿Qué documentos necesito para abrir una cuenta en MLC?", "label": "pregunta"},
    {"comment": "¿Cómo transfiero dinero desde mi cuenta a otra persona?", "label": "pregunta"}
]

# MLC store related questions
mlc_store = [
    {"comment": "¿Van a reponer arroz en la tienda de MLC de 10 y 23?", "label": "pregunta"},
    {"comment": "¿Aceptan tarjeta de crédito internacional en las tiendas Caribe?", "label": "pregunta"},
    {"comment": "¿Por qué no hay pollo en la TRD de Miramar hoy?", "label": "pregunta"},
    {"comment": "¿Cuál es el horario de atención de la tienda de MLC en Santiago?", "label": "pregunta"},
    {"comment": "¿Puedo comprar medicamentos en MLC sin receta?", "label": "pregunta"}
]

# Health related questions
health = [
    {"comment": "¿Dónde puedo encontrar ibuprofeno en La Habana?", "label": "pregunta"},
    {"comment": "¿Cómo hago para pedir cita con el especialista en el hospital Calixto García?", "label": "pregunta"},
    {"comment": "¿Por qué no hay ambulancia disponible en mi municipio?", "label": "pregunta"},
    {"comment": "¿Qué documentos necesito para llevar a mi hijo al pediatra?", "label": "pregunta"},
    {"comment": "¿Hay algún teléfono de emergencia para casos urgentes?", "label": "pregunta"}
]

# Water service related questions
water = [
    {"comment": "¿Cuándo repararán la fuga de agua en mi calle?", "label": "pregunta"},
    {"comment": "¿Por qué no llega agua a mi edificio en los últimos días?", "label": "pregunta"},
    {"comment": "¿Cómo reporto un problema con el medidor de agua?", "label": "pregunta"},
    {"comment": "¿Hay algún horario fijo para el suministro de agua en mi zona?", "label": "pregunta"},
    {"comment": "¿Qué hacer si el agua sale turbia?", "label": "pregunta"}
]

# Postal service related questions
postal = [
    {"comment": "¿Cuánto tarda en llegar una carta desde La Habana a Camagüey?", "label": "pregunta"},
    {"comment": "¿Dónde puedo reclamar un paquete que no me llegó?", "label": "pregunta"},
    {"comment": "¿Aceptan envíos internacionales en la oficina de Correos de Vedado?", "label": "pregunta"},
    {"comment": "¿Por qué no puedo rastrear mi encomienda?", "label": "pregunta"},
    {"comment": "¿Qué necesito para enviar un paquete a provincia?", "label": "pregunta"}
]

# Housing related questions
housing = [
    {"comment": "¿Cómo puedo legalizar una permuta de vivienda?", "label": "pregunta"},
    {"comment": "¿Dónde solicito un certificado de propiedad de mi casa?", "label": "pregunta"},
    {"comment": "¿Por qué no avanzan las reparaciones de mi edificio?", "label": "pregunta"},
    {"comment": "¿Qué trámites necesito para construir un cuarto adicional?", "label": "pregunta"},
    {"comment": "¿Hay algún subsidio para reparar techos dañados?", "label": "pregunta"}
]

# Other miscellaneous questions
other = [
    {"comment": "¿Cómo denuncio un problema con la recogida de basura en mi barrio?", "label": "pregunta"},
    {"comment": "¿Dónde puedo comprar gas licuado para la cocina?", "label": "pregunta"},
    {"comment": "¿Por qué no hay pan en la bodega hoy?", "label": "pregunta"},
    {"comment": "¿Cómo puedo contactar al delegado de mi zona?", "label": "pregunta"},
    {"comment": "¿Qué hago si mi carné de identidad se perdió?", "label": "pregunta"}
]

# Import pandas at the top of the file
import pandas as pd

date = '(jueves. 3 de abril de 2025)'

# List of all categories and their corresponding data
categories = [
    ('transporte', transport),
    ('eelectrica', electric),
    ('telecomicaciones', telecom),
    ('banko', bank),
    ('mlc_tienda', mlc_store),
    ('salud', health),
    ('agua', water),
    ('postal', postal),
    ('permutas', housing),
    ('otros', other)
]

# Create and save CSV files with new naming format
for name, data in categories:
    filename = f'ia-{name}{date}.csv'
    pd.DataFrame(data).to_csv(filename, index=False, encoding='utf-8')