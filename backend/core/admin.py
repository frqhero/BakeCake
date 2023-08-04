from django.contrib import admin
from .models import Cake, Level, Topping, Shape, Berry, Decor, AboutUs


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    pass


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    pass


@admin.register(Topping)
class ToppingAdmin(admin.ModelAdmin):
    pass


@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    pass


@admin.register(Berry)
class BerryAdmin(admin.ModelAdmin):
    pass


@admin.register(Decor)
class DecorAdmin(admin.ModelAdmin):
    pass


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    pass
