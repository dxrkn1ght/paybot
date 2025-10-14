from django.db import models

class Payment(models.Model):
    user = models.ForeignKey('users.Profile', on_delete=models.CASCADE)
    amount = models.BigIntegerField()
    screenshot = models.ImageField(upload_to='screenshots/', null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment {self.id} - {self.user} - {self.amount} - {self.status}"
