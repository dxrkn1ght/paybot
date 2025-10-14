from django.db import models
class Product(models.Model):
    TYPE_CHOICES = [('coin','coin'),('rank','rank')]
    name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.BigIntegerField(default=0)
    def __str__(self):
        return f"{self.name} ({self.product_type}) - {self.price}"
