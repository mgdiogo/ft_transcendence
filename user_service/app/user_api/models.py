from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.username


class TokenBlacklist(models.Model):
    token = models.CharField(max_length=500, unique=True)
    invalidated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
