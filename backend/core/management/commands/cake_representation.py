from datetime import datetime, timedelta

from telegram import MessageEntity


class CakeRepresentation:
    def __init__(self, cake):
        self.cake = cake
        self.level = cake.level
        self.shape = cake.shape
        self.topping = cake.topping
        self.berries = {berry for berry in cake.berries.all()}
        self.decors = {decor for decor in cake.decors.all()}
        self.signature = cake.signature
        current_date = datetime.now()
        tomorrow_date = current_date + timedelta(days=1)
        self.ready_at = tomorrow_date.date()
        self.timeslot = 1
        self.address = ''

    def add_signature(self, signature):
        self.signature.append(signature)

    @property
    def bold_entity(self):
        return MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=len(self.cake.title)
        )

    def __str__(self):
        main_text = f'{self.cake.title}\n{self.cake.price} руб.\n\n{self.cake.description}'
        if self.level:
            main_text += f'\n\n{self.level.title}'
        else:
            main_text += 'Количество уровней не указано'
        if self.shape:
            main_text += f'\n{self.shape.title}'
        if self.topping:
            main_text += f'\n{self.topping.title}'
        if self.berries:
            berry_names = [berry.title for berry in self.berries]
            joined_berry_names = ', '.join(berry_names)
            berry_string = f'\n\nДобавленные ягоды: {joined_berry_names}'
            main_text += berry_string
        if self.decors:
            decor_names = [decor.title for decor in self.decors]
            joined_decor_name = ', '.join(decor_names)
            decor_string = f'\n\nДобавленный декор: {joined_decor_name}'
            main_text += decor_string
        if self.signature:
            signature_string = f'\n\nДобавленная надпись: {self.signature}'
            main_text += signature_string
        return main_text
