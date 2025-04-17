from apps.classification.models import Classification
from apps.comment.models import Comment
from datetime import date, timedelta
from django.db.models import Count, Q
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
from collections import defaultdict
from django.utils import timezone

CLASSIFICATION_COLORS = {
    'criterio_general': "#8C52FF", # Era "Neutral" en el ejemplo JS
    'sugerencia': "#6FCF97",     # Era "Positivo"
    'queja': "#FCE788",         # Era "Negativo" (Puedes cambiarlo a un rojo/naranja si prefieres)
    'pregunta': "#4287F5",       # Era "Preguntas"
    'denuncia': "#6C3483",       # Era "Urgente"
    # 'ofensa' no estaba en el ejemplo JS, asignamos uno o usamos default
    'ofensa': "#FF4D4D",         # Asignando un color amarillo/naranja
    'default': "#CCCCCC"         # Color por defecto si falta alguna clasificación
}

def get_comments_by_classification_counts(): # Renombrada para el nuevo formato
    """
    Calcula el número de comentarios para cada clasificación y devuelve
    una lista de diccionarios con formato {name, value, color}.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa
              una clasificación con su nombre, número de comentarios (value),
              y un color asociado. Devuelve una lista vacía en caso de error.
              Ej: [{'name': 'sugerencia', 'value': 5, 'color': '#4DABFF'}, ...]
    """
    try:
        # 1. Anotar cada Classification con la cuenta de sus comentarios relacionados
        classification_counts_qs = Classification.objects.annotate(
            comment_count=Count('comments')  # Usando el related_name 'comments'
        ).values(
            'name',
            'comment_count'
        )

        # 2. Preparar la lista de resultados en el formato deseado
        formatted_results = []
        for item in classification_counts_qs:
            classification_name = item['name']
            comment_count = item['comment_count']

            # Obtener el color del diccionario, usando 'default' si no se encuentra
            color = CLASSIFICATION_COLORS.get(classification_name, CLASSIFICATION_COLORS['default'])

            # Añadir el diccionario formateado a la lista
            formatted_results.append({
                "name": classification_name,
                "value": comment_count,
                "color": color
            })

        # 3. Devolver la lista formateada. La vista se encargará de la Response.
        return formatted_results

    except Exception as e:
        # Loguear el error para depuración es importante
        print(f"Error en get_comments_by_classification_formatted: {e}")
        # Devolver una lista vacía para indicar un fallo
        return []

    except Exception as e:
        # Es buena idea loguear el error aquí para depuración
        print(f"Error en get_comments_by_classification_counts: {e}")
        # Devolver un diccionario vacío o None para indicar fallo a la vista llamadora
        return {}


def get_comment_statistics_with_percentages(): # Renombrado para claridad
    """
    Calcula estadísticas sobre los comentarios, incluyendo porcentajes relativos.

    Returns:
        dict: Un diccionario con las siguientes claves:
            - total_comments (int): Número total de comentarios.
            - classified_comments (int): Número de comentarios que tienen una clasificación asignada.
            - unclassified_comments (int): Número de comentarios que NO tienen clasificación.
            - urgent_comments (int): Número de comentarios clasificados como 'pregunta' o 'denuncia'.
            - new_unread_comments (int): Número de comentarios marcados como no leídos (is_read=False).
            - comments_last_month (int): Número de comentarios creados en los últimos 30 días.
            - percentage_last_month_vs_total (float): % de comentarios del último mes sobre el total.
            - percentage_classified_vs_total (float): % de comentarios clasificados sobre el total.
            - percentage_unclassified_vs_total (float): % de comentarios no clasificados sobre el total.
            - percentage_urgent_vs_classified (float): % de comentarios urgentes sobre los clasificados.
    """
    # Define los nombres de las clasificaciones consideradas urgentes
    urgent_classification_names = ['pregunta', 'denuncia']

    # Define el período para "último mes" (últimos 30 días)
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    # --- 1. Realiza la consulta de agregación para obtener las cuentas ---
    statistics_counts = Comment.objects.aggregate(
        total_comments=Count('pk'),
        classified_comments=Count('pk', filter=Q(classification__isnull=False)),
        unclassified_comments=Count('pk', filter=Q(classification__isnull=True)),
        urgent_comments=Count('pk', filter=Q(classification__name__in=urgent_classification_names)),
        new_unread_comments=Count('pk', filter=Q(is_read=False)),
        # Cuenta comentarios creados desde hace un mes hasta ahora
        comments_last_month=Count('pk', filter=Q(created_at__gte=one_month_ago))
    )

    # --- 2. Calcula los porcentajes usando las cuentas obtenidas ---
    # Usa .get(key, 0) para evitar errores si alguna cuenta fuera None (aunque Count devuelve 0)
    total = statistics_counts.get('total_comments', 0)
    classified = statistics_counts.get('classified_comments', 0)
    unclassified = statistics_counts.get('unclassified_comments', 0)
    urgent = statistics_counts.get('urgent_comments', 0)
    last_month = statistics_counts.get('comments_last_month', 0)

    # Función auxiliar para calcular porcentaje y manejar división por cero
    def calculate_percentage(numerator, denominator):
        if denominator > 0:
            return round((numerator / denominator) * 100, 1) # Redondea a 1 decimal
        return 0.0 # O 0 si prefieres entero

    percentage_last_month_vs_total = calculate_percentage(last_month, total)
    percentage_classified_vs_total = calculate_percentage(classified, total)
    percentage_unclassified_vs_total = calculate_percentage(unclassified, total)
    percentage_urgent_vs_classified = calculate_percentage(urgent, classified) # ¡Base es 'classified'!

    # --- 3. Combina las cuentas y los porcentajes en el diccionario final ---
    # Crea una copia para no modificar el diccionario original si no se desea
    final_statistics = statistics_counts.copy()
    final_statistics['percentage_last_month_vs_total'] = percentage_last_month_vs_total
    final_statistics['percentage_classified_vs_total'] = percentage_classified_vs_total
    final_statistics['percentage_unclassified_vs_total'] = percentage_unclassified_vs_total
    final_statistics['percentage_urgent_vs_classified'] = percentage_urgent_vs_classified

    return final_statistics


def get_classification_timeline(start_date=None, end_date=None, period='day'):
    """
    Genera una línea de tiempo con la frecuencia de comentarios por clasificación.
    (Docstring igual que antes)
    """
    # --- 1. Definir fechas y clasificaciones ---
    today = date.today()
    if end_date is None:
        end_date = today
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    classification_names = [
        'sugerencia', 'queja', 'pregunta', 'denuncia', 'ofensa', 'criterio_general'
    ]

    # --- 2. Seleccionar función de truncamiento de fecha ---
    if period == 'week':
        TruncClass = TruncWeek
        date_format = "%Y-W%W"
        output_date_format = lambda d: d.strftime(date_format)
    elif period == 'month':
        TruncClass = TruncMonth
        date_format = "%Y-%m"
        output_date_format = lambda d: d.strftime(date_format)
    else: # Default to 'day'
        period = 'day'
        TruncClass = TruncDate
        date_format = "%Y-%m-%d"
        output_date_format = lambda d: d.strftime(date_format)

    # --- 3. Construir la consulta de agregación ---
    queryset = Comment.objects.filter(
        classification__isnull=False,
        # Asegúrate de que el campo sea DateTimeField o DateField para que __date funcione
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        classification__name__in=classification_names
    ).annotate(
        period_start=TruncClass('created_at') # Trunca a Date
    ).values(
        'period_start', # Ya es un Date
        'classification__name'
    ).annotate(
        count=Count('id')
    ).order_by(
        'period_start'
    )

    # --- 4. Procesar los resultados para pivotar los datos ---
    timeline_data = defaultdict(lambda: {name: 0 for name in classification_names})

    for item in queryset:
        # --- CORRECCIÓN AQUÍ ---
        # item['period_start'] ya es un objeto datetime.date
        period_start_date = item['period_start']
        # -------------------------
        class_name = item['classification__name']
        count = item['count']

        if class_name in timeline_data[period_start_date]:
            timeline_data[period_start_date][class_name] = count

    # --- 5. Formatear la salida final ---
    formatted_timeline = []
    for dt in sorted(timeline_data.keys()):
        formatted_date_str = output_date_format(dt)
        date_entry = {'date': formatted_date_str}
        date_entry.update(timeline_data[dt])
        formatted_timeline.append(date_entry)

    return formatted_timeline