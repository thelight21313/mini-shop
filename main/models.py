from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=255)  # твой хэш

    def __str__(self):
        return self.username
