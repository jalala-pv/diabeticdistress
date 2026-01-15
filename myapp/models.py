from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Users(models.Model):
    name=models.CharField(max_length=100)
    dob=models.DateField()
    email=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    gender=models.CharField(max_length=100)
    photo=models.CharField(max_length=100)
    place=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    pin=models.CharField(max_length=100)
    district=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    AUTHUSER=models.OneToOneField(User,on_delete=models.CASCADE)


class complaints(models.Model):
    date = models.DateField()
    complaint = models.CharField(max_length=500)
    reply= models.CharField(max_length=500)
    status= models.CharField(max_length=100)
    USER = models.ForeignKey(Users,on_delete=models.CASCADE)

class review(models.Model):
    date = models.DateField()
    review = models.CharField(max_length=100)
    rating= models.CharField(max_length=100)
    USER = models.ForeignKey(Users,on_delete=models.CASCADE)

class logs(models.Model):
    date = models.DateField()
    time = models.TimeField()
    result= models.CharField(max_length=100)
    USER = models.ForeignKey(Users,on_delete=models.CASCADE)
