from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Usuarios

User = get_user_model()

class UsuariosSerializer(serializers.ModelSerializer):
    """Serializador para o modelo de usuário customizado."""

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'password', 'saldo', 'numero_da_sorte']

    def create(self, validated_data):
        """Cria o usuário usando create_user para salvar a senha corretamente."""
        return User.objects.create_user(**validated_data)
