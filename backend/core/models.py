from django.db import models


class Cake(models.Model):
    title = models.CharField(max_length=50)
    image_link = models.CharField(max_length=500)
    description = models.TextField()
    price = models.FloatField()

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


class AboutUs(models.Model):
    telegram = models.CharField('Telegram компании', max_length=200)
    instagram = models.CharField('Instagram компании', max_length=200)
    phone_number = models.CharField('Номер компании', max_length=20)
    address = models.CharField('Адрес компании', max_length=200)
    delivery_conditions = models.TextField()

    def __str__(self):
        return (
            self.telegram
            + '\n'
            + self.instagram
            + '\n'
            + self.phone_number
            + '\n'
            + self.address
            + '\n\n'
            + self.delivery_conditions
        )
