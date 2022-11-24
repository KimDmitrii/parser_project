from django.db import models

# Create your models here.


class Data(models.Model):
    # КОММЕНТАРИЙ: необязательное поле
    id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    # КОММЕНТАРИЙ: внешний ключ? уточнить
    product_id = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    link = models.CharField(max_length=200)
    site = models.CharField(max_length=50, default='some str')
