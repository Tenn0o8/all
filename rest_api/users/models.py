from django.db import models
from django.contrib.auth.models import AbstractUser
import jwt, datetime


# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class item(models.Model):
    name = models.CharField(max_length = 50)
    condition = models.BooleanField(default=True)
    IMEI = models.CharField(max_length = 20, unique = True)
    date = models.DateField(auto_now=True)
    owner = models.ForeignKey(User,on_delete = models.CASCADE,null=True,related_name = 'owner')
    def __str__(self):
        return f"{self.name}-{self.owner}/{self.IMEI}"

    def json(self):
        payload = {
            'id': self.id,
            'name': self.name,
        }
        return(payload)

class location(models.Model):
    lat = models.FloatField(null = True,default=20)
    lng = models.FloatField(null = True,default = 105)
    range = models.FloatField(null = True, default = 1)
    # timestamp will be update in mqtt code
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    original_item = models.ForeignKey(item,on_delete = models.CASCADE, null = True,related_name = 'item')
    def __str__(self):
        return f"({self.lat},{self.lng})-{self.timestamp}"
    def json(self):
        payload = {
            'lat': self.lat,
            'lng': self.lng,
            'timestamp': self.timestamp
        }
        return(payload)
