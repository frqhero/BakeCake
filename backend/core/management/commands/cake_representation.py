from datetime import datetime, timedelta

from telegram import MessageEntity

from ...models import Cake


class CakeRepresentation:
    def __init__(self, cake):
        self.cake = cake
        self.level = cake.level
        self.shape = cake.shape
        self.topping = cake.topping
        self.berries = {berry for berry in cake.berries.all()}
        self.decors = {decor for decor in cake.decors.all()}
        self.signature = cake.signature
        self.delivery = ''
        current_date = datetime.now()
        tomorrow_date = current_date + timedelta(days=1)
        self.ready_at = tomorrow_date.date()
        self.timeslot = 0
        self.address = ''
        self.comment = ''

    def add_signature(self, signature):
        self.signature.append(signature)

    @property
    def bold_entity(self):
        return MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=len(self.cake.title)
        )

    @property
    def delivery_method(self):
        return ('Самовывоз', 'Доставка')[self.delivery]

    @property
    def get_at(self):
        timeslot = next(
            timeslot
            for timeslot in Cake.TIMESLOTS
            if timeslot[0] == self.timeslot
        )
        date = str(self.ready_at)
        return f'{date}, {timeslot[1]}'

    def __str__(self):
        main_text = f'{self.cake.title}\n{self.cake.price} руб.\n\n{self.cake.description}'
        if self.level:
            main_text += f'\n\n{self.level.title}'
        else:
            main_text += '\n\nКоличество уровней не указано'
        if self.shape:
            main_text += f'\n{self.shape.title}'
        else:
            main_text += '\nФорма не указана'
        if self.topping:
            main_text += f'\n{self.topping.title}'
        else:
            main_text += '\nТоппинг не указан'
        if self.berries:
            berry_names = [berry.title for berry in self.berries]
            joined_berry_names = ', '.join(berry_names)
            berry_string = f'\nДобавленные ягоды: {joined_berry_names}'
            main_text += berry_string
        if self.decors:
            decor_names = [decor.title for decor in self.decors]
            joined_decor_name = ', '.join(decor_names)
            decor_string = f'\nДобавленный декор: {joined_decor_name}'
            main_text += decor_string
        if self.signature:
            signature_string = f'\nДобавленная надпись: {self.signature}'
            main_text += signature_string
        if self.delivery:
            main_text += f'\nСпособ доставки: {self.delivery_method}'
        if self.address:
            main_text += f'\nАдрес доставки: {self.address}'
        if self.ready_at and self.timeslot:
            main_text += f'\nДата получения и время получения: {self.get_at}'
        if self.comment:
            main_text += f'\nКомментарий: {self.comment}'

        return main_text
