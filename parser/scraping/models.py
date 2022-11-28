from django.db import models

# Create your models here.


class Data(models.Model):
    # КОММЕНТАРИЙ: необязательное поле
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    # КОММЕНТАРИЙ: внешний ключ? уточнить
    product_id = models.CharField(max_length=30)
    price = models.FloatField()
    link = models.CharField(max_length=200)
    site = models.CharField(max_length=50, default='some str')
