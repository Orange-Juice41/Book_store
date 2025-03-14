from django.db import models
from django.contrib.auth.models import AbstractUser

class Book(models.Model):
    objects = models.Manager()
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.title

class User(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Обычный пользователь'),
        ('admin', 'Администратор'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')