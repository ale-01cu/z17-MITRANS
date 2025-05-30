from djoser.serializers import UserCreateSerializer, UserSerializer as BaseUserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = (
            'id',
            'external_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_superuser',
            'is_staff',
            'role',
            'is_active',
            'create_at'
        )

    # Hacemos que el password no sea obligatorio
    def validate(self, attrs):
        if 'password' in attrs:
            raise serializers.ValidationError(
                {"password": "Use el endpoint específico para cambiar contraseña."}
            )
        return attrs

class UserAddSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'external_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_superuser',
            'is_staff',
            'role',
            'is_active',
            'create_at'
        )

