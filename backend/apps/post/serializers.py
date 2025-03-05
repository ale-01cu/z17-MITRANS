from rest_framework import serializers
from apps.post.models import Post
from apps.user.serializers import UserAddSerializer
from apps.comment.models import Comment
from apps.comment.serializers import CommentSerializer
from drf_spectacular.utils import extend_schema_field


class PostSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Post que incluye los comentarios relacionados
    y la información del usuario.
    """
    comments = serializers.SerializerMethodField()
    user = UserAddSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['external_id', 'content', 'created_at', 'user', 'comments']
        read_only_fields = ['external_id', 'created_at']

    @extend_schema_field(CommentSerializer(many=True))
    def get_comments(self, obj):
        """
        Obtiene y serializa los comentarios relacionados al post.
        """
        comments = obj.comment_set.all()
        return CommentSerializer(comments, many=True).data


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializador para la creación de posts que permite la inclusión
    de comentarios anidados.
    """
    comments = CommentSerializer(many=True, required=False)
    user = UserAddSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['external_id', 'content', 'created_at', 'user', 'comments']
        read_only_fields = ['external_id', 'created_at', 'user']

    def create(self, validated_data):
        """
        Crea un nuevo post y sus comentarios relacionados.
        """
        comments_data = validated_data.pop('comments', [])
        post = Post.objects.create(**validated_data)

        # Crear los comentarios asociados al nuevo post
        for comment_data in comments_data:
            print(comment_data)  # Potencialmente para depuración
            Comment.objects.create(
                post=post,
                user=validated_data['user'],
                **comment_data
            )

        return post
