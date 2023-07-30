from django.contrib import admin
from .models import Cake, Berry, Decor


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    pass


@admin.register(Berry)
class BerryAdmin(admin.ModelAdmin):
    pass


@admin.register(Decor)
class DecorAdmin(admin.ModelAdmin):
    pass
