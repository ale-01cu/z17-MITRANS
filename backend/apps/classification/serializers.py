from rest_framework import serializers
from apps.classification.models import Classification


class ClassificationSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Classification
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_id(self, obj):
        return obj.external_id



class ClassifyCommentByIdSerializer(serializers.Serializer):
    data = serializers.ListField(
        child=serializers.CharField(max_length=50),  # Cada ID debe ser una cadena de longitud máxima 50
        min_length=1,  # Asegura que la lista contenga al menos un ID
        allow_empty=False  # No se permiten listas vacías
    )


class CommentTextSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, max_length=500)  # Ajusta el max_length según necesites


class CommentInputObjectSerializer(serializers.Serializer):
    """Serializer para validar el objeto individual con id y text."""
    # Usamos CharField para id para flexibilidad, podrías usar UUIDField, IntegerField, etc.
    id = serializers.CharField(required=True, allow_blank=False)
    text = serializers.CharField(required=True, allow_blank=False, trim_whitespace=True)

class MultipleCommentObjectSerializer(serializers.Serializer):
    """Serializer para validar la lista de objetos CommentInput."""
    # El campo de entrada se llamará 'items' (puedes cambiarlo si prefieres)
    # y contendrá una lista de objetos validados por CommentInputObjectSerializer.
    items = serializers.ListField(
        child=CommentInputObjectSerializer(), # Cada elemento es validado por este serializer
        min_length=1,  # Requerir al menos un objeto en la lista
        # max_length=100 # Opcional: limitar cantidad
        allow_empty=False # La lista en sí no puede estar vacía
    )