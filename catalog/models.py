from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name
