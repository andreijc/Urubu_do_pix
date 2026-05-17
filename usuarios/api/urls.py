from django.urls import path, include
from rest_framework.routers import DefaultRouter
from usuarios.api.viewsets import UsuariosViewSet

router = DefaultRouter()
router.register(r'usuarios', UsuariosViewSet, basename='usuarios')


urlpatterns = [
    path('', include(router.urls))
]