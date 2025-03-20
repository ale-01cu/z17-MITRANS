from rest_framework import serializers
from apps.comment.models import Comment
from apps.user.serializers import UserAddSerializer
from apps.source.models import Source
from apps.comment_user_owner.models import UserOwner
from apps.comment_user_owner.serializers import UserOwnerSerializer
from apps.source.serializers import SourceSerializer
from apps.classification.serializers import ClassificationSerializer
from apps.classification.models import Classification


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    user = UserAddSerializer(read_only=True)
    classification = ClassificationSerializer(read_only=True)
    classification_id = serializers.CharField(
        max_length=50, write_only=True, required=False)

    user_owner_id = serializers.CharField(
        max_length=50, write_only=True, required=False)
    user_owner_name = serializers.CharField(
        max_length=50, write_only=True, required=False)
    user_owner = UserOwnerSerializer(read_only=True)

    source_id = serializers.CharField(max_length=50, write_only=True)
    source = SourceSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'classification',
                  'user', 'created_at', 'user_owner_id',
                  'user_owner_name', 'user_owner',
                  'source_id', 'source', 'classification_id'
                  ]

        read_only_fields = ['id', 'created_at', 'user',
                            'user_owner', 'source'
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
        classification_id = validated_data.pop('classification_id') \
            if 'classification_id' in validated_data else None

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

        if classification_id:
            try:
                classification = Classification.objects.get(external_id=classification_id)
            except classification.DoesNotExist:
                raise serializers.ValidationError(
                    "Clasificacón no encontrada con el external_id proporcionado.")
        else: classification = None

        comment = Comment.objects.create(
            user_owner=user_owner,
            source=source,
            classification=classification,
            **validated_data
        )
        return comment


    def update(self, instance, validated_data):
        # Si el campo 'id' está presente en los datos validados, lo interpretamos como external_id
        if 'user_owner_id' in validated_data:
            external_id = validated_data.pop('user_owner_id')
            try:
                # Buscamos el objeto por external_id y actualizamos la instancia
                user_owner = UserOwner.objects.get(external_id=external_id)
                instance.user_owner = user_owner
            except UserOwner.DoesNotExist:
                raise serializers.ValidationError({
                    'id': f'No existe un UserOwner con external_id={external_id}.'
                })

        elif 'user_owner_name' in validated_data:
            name = validated_data.pop('user_owner_name')
            try:
                # Buscamos el objeto por external_id y actualizamos la instancia
                user_owner, created = UserOwner.objects.get_or_create(name=name)

                if not created:
                    instance.user_owner = None
                    raise serializers.ValidationError({
                        'id': f'No se pudo crear un nuevo usuario propietario con name={name}.'
                    })

                instance.user_owner = user_owner

            except UserOwner.DoesNotExist:
                raise serializers.ValidationError({
                    'id': f'No existe un UserOwner con name={name}.'
                })

        else: instance.user_owner = None

        if 'source_id' in validated_data:
            external_id = validated_data.pop('source_id')
            try:
                # Buscamos el objeto por external_id y actualizamos la instancia
                source = Source.objects.get(external_id=external_id)
                instance.source = source
            except Source.DoesNotExist:
                raise serializers.ValidationError({
                    'id': f'No existe un source con external_id={external_id}.'
                })

        if 'classification_id' in validated_data:
            external_id = validated_data.pop('classification_id')
            try:
                # Buscamos el objeto por external_id y actualizamos la instancia
                classification = Classification.objects.get(external_id=external_id)
                instance.classification = classification
            except Classification.DoesNotExist:
                raise serializers.ValidationError({
                    'id': f'No existe una clasificación con external_id={external_id}.'
                })

        # Actualizamos la instancia con los datos validados
        return super().update(instance, validated_data)


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

        if instance.classification_id:
            representation['classification'] = ClassificationSerializer(
                Classification.objects.get(id=instance.classification_id)
            ).data
        else: representation['classification'] = None

        return representation



class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class ClassificationsByCommentsSerializer(serializers.Serializer):
    data = serializers.DictField(
        child=serializers.IntegerField(),
        allow_empty=False
    )