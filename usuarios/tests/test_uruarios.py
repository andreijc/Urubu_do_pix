import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Usuarios

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def usuario_teste():
    return User.objects.create(username='Paulo', password='1234',saldo=1000.00, numero_da_sorte=3)

@pytest.mark.django_db
def test_deve_criar_um_usuario_com_sucesso(api_client):
    dados_novo_usuario = {
        'username':'Paulo', 
        'password':'SenhaUltraFo99988##',
        'saldo': 1000.00,
        'numero_da_sorte':3
    }

    response = api_client.post('/api/usuarios/', dados_novo_usuario, format='json')

    print(f'Esse é p erro{response.data}')

    assert response.status_code == status.HTTP_201_CREATED
    assert Usuarios.objects.count() == 1
    assert Usuarios.objects.first().username == 'Paulo'

@pytest.mark.django_db
def test_quando_usuario_colocar_nome_e_senha_certos_faz_login(api_client):
    entrada = {
        'username':'Paulo',
        'password':'SenhaUltraFo99988##'
    }

    response = api_client.post('/api/usuarios/login/', entrada, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert reponse.data['user' == entrada['nome']]



