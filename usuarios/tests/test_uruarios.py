import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Usuarios

User = get_user_model()

@pytest.fixture
def api_client():
    """Cliente de teste do DRF para chamadas à API."""
    return APIClient()

@pytest.fixture
def usuario_teste():
    """Usuário que inicia a transferência."""
    return User.objects.create(username='Paulo', password='1234', saldo=100.00, numero_da_sorte=3)

@pytest.fixture
def usuario_destino():
    """Usuário que recebe a transferência."""
    return User.objects.create(username='Maria', password='4321', saldo=50.00, numero_da_sorte=7)

@pytest.mark.django_db
def test_deve_criar_um_usuario_com_sucesso(api_client):
    """Verifica se a API cria um usuário com sucesso."""
    dados_novo_usuario = {
        'username':'Paulo', 
        'password':'SenhaUltraFo99988##',
        'saldo': 1000.00,
        'numero_da_sorte':3
    }

    response = api_client.post('/api/usuarios/', dados_novo_usuario, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Usuarios.objects.count() == 1
    assert Usuarios.objects.first().username == 'Paulo'

@pytest.mark.django_db
def test_quando_usuario_colocar_nome_e_senha_certos_faz_login(api_client):
    """Cria um usuário válido e confirma que o login retorna tokens."""
    User.objects.create_user(
        username='Paulo',
        password='SenhaUltraFo99988##',
        saldo=1000.00,
        numero_da_sorte=3
    )

    entrada = {
        'username':'Paulo',
        'password':'SenhaUltraFo99988##'
    }

    response = api_client.post('/api/usuarios/login/', entrada, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert response.data['user'] == entrada['username']


@pytest.mark.django_db
def test_transferencia_entre_usuarios_deve_atualizar_saldos(api_client, usuario_teste, usuario_destino):
    """Verifica se a transferência entre dois usuários atualiza corretamente os saldos."""
    api_client.force_authenticate(user=usuario_teste)

    dados_transferencia = {
        'destinatario_id': usuario_destino.id,
        'valor': 40.00
    }

    response = api_client.post('/api/usuarios/transferir/', dados_transferencia, format='json')

    assert response.status_code == status.HTTP_200_OK

    usuario_teste.refresh_from_db()
    usuario_destino.refresh_from_db()

    assert usuario_teste.saldo == 60.00
    assert usuario_destino.saldo == 90.00
    assert response.data['mensagem'] == 'Transferência realizada com sucesso.'

