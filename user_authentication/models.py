from django.db import models
from sorl.thumbnail import ImageField

class Profile(models.Model):
    username = models.CharField(max_length=100)
    image = ImageField(upload_to="photoshare_image/profile",
        default="https://res.cloudinary.com/parneetsingh/image/upload/v1/photoshare_image/profile/blank-profile-picture-973460_640_gu5g1r",
        blank=True
    )
    def __str__(self):
         return self.username



class Post(models.Model):
    username = models.CharField(max_length=100)
    image = ImageField(upload_to="photoshare_image/posts",blank=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.username
