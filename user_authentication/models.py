from django.db import models
from sorl.thumbnail import ImageField

class Profile(models.Model):
    username = models.CharField(max_length=100)
    image = ImageField(upload_to="photoshare_image/profile",
        default="https://res.cloudinary.com/parneetsingh/image/upload/v1628080124/photoshare_image/profile/blank-profile-picture-973460_1280_szji3x.png",
        blank=True
    )
    disabled = models.BooleanField(default=False)
    private = models.BooleanField(default=False)


    def __str__(self):
         return self.username



class Post(models.Model):
    username = models.CharField(max_length=100)
    image = ImageField(upload_to="photoshare_image/posts",blank=True)
    likes = models.IntegerField(default=0)
    commentDisable = models.BooleanField(default=False)
    description = models.CharField(max_length=500,default='')

    def __str__(self):
        return self.username
