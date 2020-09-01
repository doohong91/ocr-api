from datetime import datetime
import os

from django.db import models


def set_filename_format(now, instance, filename):
    """ 
    file format setting 
    e.g)
        {date}-{microsecond}{extension} 
        2020-08-19-158859.png 
    """
    return "{date}-{microsecond}{extension}".format(
        date=str(now.date()), microsecond=now.microsecond, extension=os.path.splitext(filename)[1],
    )


def user_directory_path(instance, filename):
    """ 
    image upload directory setting
    e.g) 
        images/{year}/{month}/{day}/{filename} 
        images/2020/8/19/2020-08-19-158859.png 
    """
    now = datetime.now()
    path = "images/{year}/{month}/{day}/{filename}".format(
        year=now.year,
        month=now.month,
        day=now.day,
        filename=set_filename_format(now, instance, filename),
    )
    return path


class Image(models.Model):
    original_img = models.ImageField(upload_to=user_directory_path)
    result_img = models.ImageField(upload_to=user_directory_path)
    bounding_boxes = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
