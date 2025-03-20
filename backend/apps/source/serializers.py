from rest_framework import serializers
from .models import Source

class SourceSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = Source
        fields = ('id', 'name', 'url', 'description', 'created_at')

    def get_id(self, obj):
        return obj.external_id


class SourceIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('id',)
