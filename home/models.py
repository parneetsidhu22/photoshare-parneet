from django.db import models

class Friend(models.Model):
    follower = models.CharField(max_length=100)
    followed = models.CharField(max_length=100)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.follower + "--->" + self.followed

class Likes(models.Model):
    postid = models.IntegerField()
    username = models.CharField(max_length=100)

    def __str__(self):
        return "Like by: " + self.username

class Comment(models.Model):
    postid = models.IntegerField()
    username = models.CharField(max_length=100)
    comment = models.CharField(max_length=500)
    time_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "By: " + self.username