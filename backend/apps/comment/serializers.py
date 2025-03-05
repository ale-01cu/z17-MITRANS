from rest_framework import serializers
from apps.comment.models import Comment
from apps.user.serializers import UserAddSerializer


class CommentSerializer(serializers.ModelSerializer):
    user = UserAddSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['external_id', 'text', 'classification', 'user', 'created_at']
        read_only_fields = ['external_id', 'created_at', "user"]



class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
