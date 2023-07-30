from django.db import models


class Cake(models.Model):
    title = models.CharField(max_length=50)
    image_link = models.CharField(max_length=500)
    description = models.TextField()

    def __str__(self):
        return self.title


class Berry(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Decor(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title
