from django.db import models
class Profile(models.Model):
    tg_id = models.BigIntegerField(unique=True)
    nick = models.CharField(max_length=100, blank=True, null=True)
    lang = models.CharField(max_length=4, default='uz')
    balance = models.BigIntegerField(default=0)
    def __str__(self):
        return f"{self.tg_id} - {self.nick or ''}"
