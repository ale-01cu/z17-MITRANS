from rest_framework import serializers
from apps.classification.models import Classification


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ['external_id', 'name', 'created_at']