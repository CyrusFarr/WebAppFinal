from django.conf import settings
from django.db import models


# Create your models here.
class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)


class Meta:
    constraints = [
        models.UniqueConstraint(fields=["user", "symbol"], name="unique_user_stock")
    ]


def __str__(self):
    return f"{self.user.username} - {self.symbol}"
