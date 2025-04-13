from rest_framework import serializers


class MultipleFileUploadSerializer(serializers.Serializer):
    # Espera una lista de archivos bajo la clave 'files'
    # Ajusta max_length según necesites (o quítalo si no hay límite)
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False, use_url=False),
        max_length=10, # Opcional: limita el número de archivos por request
        min_length=1 # Opcional: requiere al menos un archivo
    )
