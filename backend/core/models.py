from django.db import models
from telegram import MessageEntity


class Cake(models.Model):
    title = models.CharField(max_length=50)
    image_link = models.CharField(max_length=500)
    description = models.TextField()
    price = models.FloatField(default=0)
    level = models.ForeignKey('Level', on_delete=models.CASCADE, null=True, blank=True)
    shape = models.ForeignKey('Shape', on_delete=models.CASCADE, null=True, blank=True)
    topping = models.ForeignKey('Topping', on_delete=models.CASCADE, null=True, blank=True)
    berries = models.ManyToManyField('Berry', blank=True, symmetrical=False)
    decors = models.ManyToManyField('Decor', related_name='decors', blank=True)
    signature = models.CharField(max_length=100, blank=True)
    TIMESLOTS = (
        (1, '10-12'),
        (2, '12-14'),
        (3, '14-16'),
        (4, '16-18'),
        (5, '18-20'),
    )
    timeslot = models.IntegerField(choices=TIMESLOTS, default=1)
    DELIVERY_CHOICES = (
        (0, 'Самовывоз'),
        (1, 'Доставка'),
    )
    delivery = models.IntegerField(choices=DELIVERY_CHOICES, default=0)
    ready_at = models.DateField(null=True, blank=True, default=None)
    address = models.CharField(max_length=500, default='', blank=True)
    comment = models.CharField(max_length=500, default='', blank=True)
    STATUSES = (
        (1, 'Новый'),
        (2, 'Отменен'),
        (3, 'Приготовить'),
        (4, 'Доставить'),
        (5, 'Выполнен'),
        (6, 'Образец'),
    )
    status = models.IntegerField(choices=STATUSES, default=1)

    def __str__(self):
        main_text = f'{self.title}\n{self.price} руб.\n\n{self.description}'
        berries = self.berries.all()
        decors = self.decors.all()
        if self.level:
            main_text += f'\n\n{self.level.title}'
        else:
            main_text += 'Количество уровней не указано'
        if self.shape:
            main_text += f'\n{self.shape.title}'
        if self.topping:
            main_text += f'\n{self.topping.title}'
        if berries:
            berry_names = [berry.title for berry in berries]
            joined_berry_names = ', '.join(berry_names)
            berry_string = f'\n\nДобавленные ягоды: {joined_berry_names}'
            main_text += berry_string
        if decors:
            decor_names = [decor.title for decor in decors]
            joined_decor_name = ', '.join(decor_names)
            decor_string = f'\n\nДобавленный декор: {joined_decor_name}'
            main_text += decor_string
        if self.signature:
            signature_string = f'\n\nДобавленная надпись: {self.signature}'
            main_text += signature_string
        return main_text


class Level(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)
    price = models.FloatField(default=0)


class Shape(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)
    price = models.FloatField(default=0)


class Topping(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)
    price = models.FloatField(default=0)


class Berry(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)
    price = models.FloatField(default=0)

    def __str__(self):
        return self.title


class Decor(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)
    title = models.CharField(max_length=50)
    price = models.FloatField(default=0)

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
