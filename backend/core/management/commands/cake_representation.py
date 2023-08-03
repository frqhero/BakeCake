from telegram import MessageEntity


class CakeRepresentation:
    def __init__(self, cake):
        self.cake = cake
        self.berries = []
        self.decor = []
        self.signature = []

    def add_signature(self, signature):
        self.signature.append(signature)

    @property
    def bold_entity(self):
        return MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=len(self.cake.title)
        )

    def __str__(self):
        main_text = f'{self.cake.title}\n{self.cake.price} руб.\n\n{self.cake.description}'
        if self.berries:
            berry_names = [berry.title for berry in self.berries]
            joined_berry_names = ', '.join(berry_names)
            berry_string = f'\n\nДобавленные ягоды: {joined_berry_names}'
            main_text += berry_string
        if self.decor:
            decor_names = [decor.title for decor in self.decor]
            joined_decor_name = ', '.join(decor_names)
            decor_string = f'\n\nДобавленный декор: {joined_decor_name}'
            main_text += decor_string
        if self.signature:
            joined_signatures = ', '.join(self.signature)
            signature_string = f'\n\nДобавленные надписи: {joined_signatures}'
            main_text += signature_string
        return main_text
