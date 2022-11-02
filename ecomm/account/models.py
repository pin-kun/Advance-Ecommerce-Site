from email.policy import default
from pyexpat import model
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() # Will always return currently logged in user

# Create your models here.
class Customer(models.Model):
    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    id_user = models.IntegerField()
    profileimg = models.ImageField(upload_to="profile_images", default="blank-profile-picture.png")

    def __str__(self):
        return self.user.username
