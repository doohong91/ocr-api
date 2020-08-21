from datetime import datetime
import os
from django.db import models


def set_filename_format(now, instance, filename):
    """ file format setting 
     e.g)
        {username}-{date}-{microsecond}{extension} 
        hjh-2016-07-12-158859.png """
    return "{username}-{date}-{microsecond}{extension}".format(
        username=instance.user.username,
        date=str(now.date()),
        microsecond=now.microsecond,
        extension=os.path.splitext(filename)[1],
    )


def user_directory_path(instance, filename):
    """ image upload directory setting
    e.g) 
        images/{year}/{month}/{day}/{username}/{filename} 
        images/2016/7/12/hjh/hjh-2016-07-12-158859.png """
    now = datetime.now()
    path = "images/{year}/{month}/{day}/{username}/{filename}".format(
        year=now.year,
        month=now.month,
        day=now.day,
        username=instance.user.username,
        filename=set_filename_format(now, instance, filename),
    )
    return path


class Image(models.Model):
    img = models.ImageField(upload_to=user_directory_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
