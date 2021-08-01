from django.db import models
from django.utils import timezone


class cidade(models.Model):

    cidade_origem = models.CharField(max_length=200)
    cidade_destino = models.CharField(max_length=200)
    distancia =  models.IntegerField(blank = True)
    long = models.CharField(max_length=200)
    lati = models.CharField(max_length=200)
    ativo= models.BooleanField(default=True)

    def __str__(self):
        return self.cidade_origem    


class rota(models.Model):
    nome_rota = models.CharField(max_length=200)
    cidade  =  models.CharField(max_length=200)
    primeiro = models.BooleanField(default=False)
    sequecia = models.IntegerField(blank = True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_rota
    

        