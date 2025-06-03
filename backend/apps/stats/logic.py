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

def get_comments_by_classification_counts(user):
    """
    Calcula el número de comentarios para cada clasificación, filtrando por la entidad del usuario,
    y devuelve una lista de diccionarios con formato {name, value, color}.

    Args:
        user: El usuario autenticado (debe tener el campo 'entity')

    Returns:
        list: Una lista de diccionarios con el formato:
              [{'name': 'sugerencia', 'value': 5, 'color': '#4DABFF'}, ...]
              Devuelve lista vacía en caso de error.
    """
    try:
        # Filtro base: solo comentarios de la entidad del usuario (si no es superusuario)
        # if user.entity is None return empty list
        base_filter = {}

        if not user.is_superuser and hasattr(user, 'entity') and user.entity:
            base_filter = {'comments__user_owner__entity': user.entity}

        # 1. Anotar cada Classification con la cuenta de comentarios (filtrados por entidad)
        classification_counts_qs = Classification.objects.annotate(
            comment_count=Count(
                'comments',
                filter=Q(**base_filter)  # Aplicamos el filtro aquí
            )
        ).values(
            'name',
            'comment_count'
        )

        # 2. Preparar los resultados en el formato deseado
        formatted_results = []
        for item in classification_counts_qs:
            classification_name = item['name']
            comment_count = item['comment_count']

            # Saltar clasificaciones con 0 comentarios (opcional)
            if comment_count == 0:
                continue

            color = CLASSIFICATION_COLORS.get(classification_name, CLASSIFICATION_COLORS['default'])

            formatted_results.append({
                "name": classification_name,
                "value": comment_count,
                "color": color
            })

        return formatted_results

    except Exception as e:
        print(f"Error en get_comments_by_classification_counts: {e}")
        return []  # Devuelve lista vacía en caso de error


def get_comment_statistics_with_percentages(user):
    """
    Calcula estadísticas sobre los comentarios de la misma entidad que el usuario,
    incluyendo porcentajes relativos.

    Args:
        user: El usuario autenticado (debe tener el campo 'entity')

    Returns:
        dict: Un diccionario con estadísticas filtradas por entidad.
    """
    # Define los nombres de las clasificaciones consideradas urgentes
    urgent_classification_names = ['pregunta', 'denuncia']

    # Define el período para "último mes" (últimos 30 días)
    now = timezone.now()
    one_month_ago = now - timedelta(days=30)

    # Filtro base: solo comentarios de la entidad del usuario (si no es superusuario)
    # if user.entity is None return empty value
    base_filter = Q()

    if not user.is_superuser and hasattr(user, 'entity') and user.entity:
        base_filter = Q(user_owner__entity=user.entity)

    # --- 1. Realiza la consulta de agregación con filtro por entidad ---
    statistics_counts = Comment.objects.filter(base_filter).aggregate(
        total_comments=Count('pk'),
        classified_comments=Count('pk', filter=Q(classification__isnull=False)),
        unclassified_comments=Count('pk', filter=Q(classification__isnull=True)),
        urgent_comments=Count('pk', filter=Q(classification__name__in=urgent_classification_names)),
        new_unread_comments=Count('pk'),
        comments_last_month=Count('pk', filter=Q(created_at__gte=one_month_ago))
    )

    # --- 2. Calcula los porcentajes ---
    total = statistics_counts.get('total_comments', 0)
    classified = statistics_counts.get('classified_comments', 0)
    unclassified = statistics_counts.get('unclassified_comments', 0)
    urgent = statistics_counts.get('urgent_comments', 0)
    last_month = statistics_counts.get('comments_last_month', 0)
    new_unread = statistics_counts.get('new_unread_comments', 0)

    def calculate_percentage(numerator, denominator):
        return round((numerator / denominator) * 100, 1) if denominator > 0 else 0.0

    # --- 3. Prepara el diccionario final ---
    final_statistics = {
        'total_comments': total,
        'classified_comments': classified,
        'unclassified_comments': unclassified,
        'urgent_comments': urgent,
        'new_unread_comments': new_unread,
        'comments_last_month': last_month,
        'percentage_last_month_vs_total': calculate_percentage(last_month, total),
        'percentage_classified_vs_total': calculate_percentage(classified, total),
        'percentage_unclassified_vs_total': calculate_percentage(unclassified, total),
        'percentage_urgent_vs_classified': calculate_percentage(urgent, classified),
    }

    return final_statistics


def get_classification_timeline(user, start_date=None, end_date=None, period='day'):
    """
    Genera una línea de tiempo con la frecuencia de comentarios por clasificación,
    filtrada por la entidad del usuario.

    Args:
        user: El usuario autenticado (debe tener el campo 'entity')
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        period: Periodo de agrupación ('day', 'week' o 'month')

    Returns:
        list: Lista de diccionarios con la frecuencia de comentarios por periodo y clasificación
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
    else:  # Default to 'day'
        period = 'day'
        TruncClass = TruncDate
        date_format = "%Y-%m-%d"
        output_date_format = lambda d: d.strftime(date_format)

    # --- 3. Construir la consulta con filtro por entidad ---
    base_filter = Q(classification__isnull=False,
                    created_at__date__gte=start_date,
                    created_at__date__lte=end_date,
                    classification__name__in=classification_names)

    # Añadir filtro por entidad si el usuario no es superusuario
    # if user.entity is None return empty value
    base_filter &= Q()

    if not user.is_superuser and hasattr(user, 'entity') and user.entity:
        base_filter &= Q(user_owner__entity=user.entity)

    queryset = Comment.objects.filter(base_filter).annotate(
        period_start=TruncClass('created_at')
    ).values(
        'period_start',
        'classification__name'
    ).annotate(
        count=Count('id')
    ).order_by(
        'period_start'
    )

    # --- 4. Procesar los resultados para pivotar los datos ---
    timeline_data = defaultdict(lambda: {name: 0 for name in classification_names})

    for item in queryset:
        period_start_date = item['period_start']
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