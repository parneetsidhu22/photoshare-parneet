# Generated by Django 3.2.4 on 2021-07-16 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_authentication', '0006_rename_posts_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='commentDisable',
            field=models.BooleanField(default=False),
        ),
    ]