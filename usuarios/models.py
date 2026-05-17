from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Usuarios(AbstractUser):
    
    saldo = models.FloatField()
    numero_da_sorte = models.IntegerField()
    