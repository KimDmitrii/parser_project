from django.db import models

# Create your models here.


class Data(models.Model):
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    id = models.IntegerField(primary_key=True)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    link = models.CharField(max_length=200)
    site = models.CharField(max_length=50, default='some str')
