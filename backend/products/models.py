from django.db import models

class Product(models.Model):
    TYPE_CHOICES = [
        ("coin","Coin"),
        ("rank","Rank"),
    ]
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=50, unique=True)  # e.g. COIN_10, RANK_VIP
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.PositiveIntegerField(help_text="price in som (integer)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.price} som"
