# Generated by Django 4.2.3 on 2023-07-30 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_berry'),
    ]

    operations = [
        migrations.AddField(
            model_name='berry',
            name='slug',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]