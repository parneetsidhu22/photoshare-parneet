from django.db import models

class Profile(models.Model):
    username = models.CharField(max_length=100)
    image = models.ImageField(upload_to="photoshare_image/profile",
        default="https://res.cloudinary.com/parneetsingh/image/upload/v1/photoshare_image/profile/blank-profile-picture-973460_640_gu5g1r",
        blank=True
    )
