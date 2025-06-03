from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from .models import UserAccount
from .serializers import UserSerializer

class UserAccountListView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated] # Solo usuarios autenticados pueden acceder

    def get_queryset(self):
        """
        Este método es llamado para obtener el queryset base.
        Lo sobrescribimos para filtrar los usuarios según la entidad del solicitante.
        """
        user = self.request.user

        # Si el usuario es un superusuario, puede ver todas las cuentas
        if user.is_superuser:
            return UserAccount.objects.all().select_related('entity').order_by('username')

        # Si el usuario no es superusuario, filtramos por su entidad
        # Primero, verificamos si el usuario tiene una entidad asignada
        if hasattr(user, 'entity') and user.entity:
            # Devolvemos solo los usuarios que pertenecen a la misma entidad que el usuario solicitante
            return UserAccount.objects.filter(entity=user.entity).select_related('entity').order_by('username')
        else:
            # Si el usuario no es superusuario y no tiene una entidad asignada,
            # no debería poder ver ninguna lista de usuarios (o quizás solo a sí mismo,
            # pero para una lista de "otros usuarios" es más seguro no mostrar nada).
            # O podrías levantar una PermissionDenied si esto no debería ocurrir.
            return UserAccount.objects.none() # Devuelve un queryset vacío
            # Alternativa: Solo mostrarse a sí mismo (si este endpoint también sirviera para eso)
            # return UserAccount.objects.filter(pk=user.pk).select_related('entity')