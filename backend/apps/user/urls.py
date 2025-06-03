from django.urls import path
from .views import UserAccountListView

urlpatterns = [
    path('', UserAccountListView.as_view(), name='users'),
]