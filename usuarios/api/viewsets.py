from django.contrib.auth import authenticate, get_user_model
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.models import Usuarios
from .serializers import UsuariosSerializer

User = get_user_model()

class UsuariosViewSet(viewsets.ModelViewSet):
    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer

    # Define que qualquer um pode se logar ou cadastrar
    def get_permissions(self):
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        # authentica o usuario
        user = authenticate(username=username, password=password)

        if user is not None:
            # Se existe gera um token

            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'acess': str(refresh.acess_token),
                'user': user.username
                },
                status=status.HTTP_200_OK
                )
        return Response({
            'error':'Credenciais invalidas'
            },
            status=status.HTTP_401_UNAUTHORIZED
            )

    