# Generated by Django 4.2.3 on 2023-07-30 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cake_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Berry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
            ],
        ),
    ]
