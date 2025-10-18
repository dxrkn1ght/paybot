from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS = [
        ("pending","Pending"),
        ("paid","Paid"),
        ("delivered","Delivered"),
        ("canceled","Canceled"),
    ]
    user_id = models.BigIntegerField()  # Telegram user id
    user_nick = models.CharField(max_length=120, blank=True)
    product_code = models.CharField(max_length=100)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} {self.product_code} ({self.amount})"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    sender_account = models.CharField(max_length=200, blank=True)
    amount = models.PositiveIntegerField()
    screenshot = models.ImageField(upload_to="payments/", blank=True, null=True)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment #{self.id} for Order #{self.order.id}"
