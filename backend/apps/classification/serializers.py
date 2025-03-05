from rest_framework import serializers
from apps.classification.models import Classification


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ['external_id', 'name', 'created_at']


class ClassifyCommentByIdSerializer(serializers.Serializer):
    data = serializers.ListField(
        child=serializers.CharField(max_length=50),  # Cada ID debe ser una cadena de longitud máxima 50
        min_length=1,  # Asegura que la lista contenga al menos un ID
        allow_empty=False  # No se permiten listas vacías
    )