from telegram import InlineKeyboardButton

MAIN_LAYOUT = [
        [
            InlineKeyboardButton(
                text='Готовый', callback_data=str('COMPLETE_CAKE')
            ),
            InlineKeyboardButton(
                text='Соберите свой', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(text='О нас', callback_data=str('ABOUT_US')),
        ],
    ]

title = 'Добро пожаловать в Bake Cake!'
info = 'В нашем магазине вы можете выбрать готовый торт или собрать свой!'

WELCOME_TEXT = title + '\n\n' + info
