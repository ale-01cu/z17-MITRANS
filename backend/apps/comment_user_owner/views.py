from datetime import timedelta
from django.shortcuts import render
from rest_framework import generics, viewsets
from .serializers import UserOwnerSerializer
from .models import UserOwner
from .pagination import ResultsSetPagination
from rest_framework.permissions import IsAuthenticated  # Requiere autenticación
from django.utils.timezone import now  # Import correcto
from rest_framework.exceptions import NotFound
from django.db.models import Q
import django_filters

class UserOwnerFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = UserOwner
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(email__icontains=value) |
            Q(phone_number__icontains=value) |
            Q(province__icontains=value)
        )

# Create your views here.
class ListUserOwnerView(generics.ListAPIView):
    pagination_class = ResultsSetPagination
    permission_classes = [IsAuthenticated]  # Requiere autenticación

    queryset = UserOwner.objects.all().order_by('-created_at')
    serializer_class = UserOwnerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user

        # 1. Filtro por entidad del usuario autenticado (si no es superusuario)
        if not user.is_superuser:
            if hasattr(user, 'entity') and user.entity:
                queryset = queryset.filter(entity=user.entity).select_related('entity')
            else:
                return queryset.none()

        # 2. Filtro opcional por horas
        hours = self.request.query_params.get('last_hours')
        if hours:
            try:
                hours = int(hours)
                time_threshold = now() - timedelta(hours=hours)
                queryset = queryset.filter(created_at__gte=time_threshold)
            except ValueError:
                pass

        # 3. Filtro de búsqueda
        search_term = self.request.query_params.get("search", "").strip()
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(email__icontains=search_term) |
                Q(phone_number__icontains=search_term) |
                Q(province__icontains=search_term)
            )

        return queryset


class UpdateUserOwnerView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]  # Requiere autenticación
    queryset = UserOwner.objects.all()
    serializer_class = UserOwnerSerializer

    def get_queryset(self):
        """
        Restringir los objetos editables al usuario autenticado.
        Similar a tu ListUserOwnerView.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return queryset

        if hasattr(user, 'entity') and user.entity:
            return queryset.filter(entity=user.entity)
        else:
            return queryset.none()


    def get_object(self):
        """
        Busca el objeto usando external_id en lugar de id
        """
        queryset = self.get_queryset()
        external_id = self.kwargs["pk"]  # Viene de la URL

        try:
            obj = queryset.get(external_id=external_id)
        except UserOwner.DoesNotExist:
            raise NotFound("Usuario emisor no encontrado.")

        return obj

