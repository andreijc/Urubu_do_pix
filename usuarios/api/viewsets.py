from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from usuarios.models import Usuarios
from .serializers import UsuariosSerializer

User = get_user_model()

class UsuariosViewSet(viewsets.ModelViewSet):
    """ViewSet que controla as operações de usuário e a transferência de saldo."""

    queryset = Usuarios.objects.all()
    serializer_class = UsuariosSerializer

    def get_permissions(self):
        """Define permissões: criar/login são públicas; demais ações exigem autenticação."""
        if self.action in ['create', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def varificar_saldo_valido(self, saldo, valor):
        if saldo < valor:
            return Response({'error': 'Saldo insuficiente.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login(self, request):
        """Autentica o usuário e retorna tokens JWT para o login."""
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user.username
                },
                status=status.HTTP_200_OK
                )
        return Response({
            'error':'Credenciais invalidas'
            },
            status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'])
    def transferir(self, request):
        """Processa uma transferência de saldo entre dois usuários autenticados."""
        remetente = request.user
        destinatario_id = request.data.get('destinatario_id')
        valor = request.data.get('valor')

        try:
            destinatario_id = int(destinatario_id)
        except (TypeError, ValueError):
            return Response({'error': 'ID de destinatário inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return Response({'error': 'Valor inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if valor <= 0:
            return Response({'error': 'O valor de transferência deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)

        if remetente.id == destinatario_id:
            return Response({'error': 'Não é possível transferir para a mesma conta.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            destinatario = Usuarios.objects.get(pk=destinatario_id)
        except Usuarios.DoesNotExist:
            return Response({'error': 'Destinatário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        error_response = self.varificar_saldo_valido(remetente.saldo, valor)
        if error_response:
            return error_response

        with transaction.atomic():
            remetente.saldo -= valor
            destinatario.saldo += valor
            remetente.save(update_fields=['saldo'])
            destinatario.save(update_fields=['saldo'])

        return Response({
            'mensagem': 'Transferência realizada com sucesso.',
            'saldo_remetente': remetente.saldo,
            'saldo_destinatario': destinatario.saldo
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def fazer_pix(self, request):
        usuario = request.user
        valor = request.data.get('valor')

        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return Response({'error': 'Valor inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if valor <= 0:
            return Response({'error': 'O valor de PIX deve ser maior que zero.'}, status=status.HTTP_400_BAD_REQUEST)

        error_response = self.varificar_saldo_valido(usuario.saldo, valor)
        if error_response:
            return error_response

        valor_pix = valor * 10
        usuario.saldo = valor_pix
        usuario.save(update_fields=['saldo'])

        return Response({'mensagem': 'Pix feito com sucesso.', 'saldo': usuario.saldo}, status=status.HTTP_200_OK)
