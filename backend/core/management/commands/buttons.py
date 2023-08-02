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

CUSTOMIZATION_LAYOUT = [
        [
            InlineKeyboardButton(
                text='Добавить ягоды', callback_data=str('berries')
            ),
            InlineKeyboardButton(
                text='Добавить декор', callback_data=str('decor')
            ),
            InlineKeyboardButton(
                text='Сделать надпись', callback_data=str('signature')
            ),
        ],
        [
            InlineKeyboardButton(
                text='Перейти к оформлению заказа',
                callback_data=str('check_out'),
            ),
        ],
    ]
