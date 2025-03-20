from rest_framework import serializers
from apps.comment.models import Comment
from apps.user.serializers import UserAddSerializer
from apps.source.models import Source
from apps.comment_user_owner.models import UserOwner
from apps.comment_user_owner.serializers import UserOwnerSerializer
from apps.source.serializers import SourceSerializer


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    user = UserAddSerializer(read_only=True)

    user_owner_id = serializers.CharField(max_length=50, write_only=True, required=False)
    user_owner_name = serializers.CharField(max_length=50, write_only=True, required=False)
    user_owner_detail = UserOwnerSerializer(read_only=True)

    source_id = serializers.CharField(max_length=50, write_only=True)
    source_detail = SourceSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'classification',
                  'user', 'created_at', 'user_owner_id',
                  'user_owner_name', 'user_owner_detail',
                  'source_id', 'source_detail'
                  ]

        read_only_fields = ['id', 'created_at', 'user',
                            'user_owner_detail', 'source_detail'
                            ]


    def get_id(self, obj):
        return obj.external_id


    def create(self, validated_data):
        # Extrae los datos de user_owner y source
        user_owner_id = validated_data.pop('user_owner_id') \
            if 'user_owner_id' in validated_data else None
        user_owner_name = validated_data.pop('user_owner_name') \
            if 'user_owner_name' in validated_data else None
        source_data = validated_data.pop('source_id')

        if user_owner_id: user_owner_data = user_owner_id
        elif user_owner_name: user_owner_data = user_owner_name
        else: user_owner_data = None

        # Manejo de user_owner
        user_owner = None
        if user_owner_data:
            try:
                user_owner = UserOwner.objects.get(external_id=user_owner_data)
            except UserOwner.DoesNotExist:
                # raise serializers.ValidationError("UserOwner no encontrado con el external_id proporcionado.")
                user_owner, created = UserOwner.objects.get_or_create(name=user_owner_data)
        else:
            print("Falta el user owner")

        # Manejo de source
        try:
            source = Source.objects.get(external_id=source_data)
        except Source.DoesNotExist:
            raise serializers.ValidationError(
                "Source no encontrado con el external_id proporcionado.")

        # Crea el objeto Comment con los objetos relacionados
        comment = Comment.objects.create(
            user_owner=user_owner,
            source=source,
            **validated_data
        )
        return comment


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.source_id:
            representation['source_detail'] = SourceSerializer(
                Source.objects.get(id=instance.source_id)).data
        else: representation['source_detail'] = None

        if instance.user_owner_id:
            representation['user_owner'] = UserOwnerSerializer(
                UserOwner.objects.get(id=instance.user_owner_id)).data

        else: representation['user_owner'] = None
        return representation



class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ClassificationsByCommentsSerializer(serializers.Serializer):
    data = serializers.DictField(
        child=serializers.IntegerField(),
        allow_empty=False
    )