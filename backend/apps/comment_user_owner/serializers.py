from rest_framework import serializers
from .models import UserOwner

class UserOwnerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = UserOwner
        fields = ('id', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_id(self, obj):
        return obj.external_id
