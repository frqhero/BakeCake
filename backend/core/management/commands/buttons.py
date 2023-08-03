from random import choice

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_LAYOUT = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text='Готовый', callback_data=str('COMPLETE_CAKE')
            ),
            InlineKeyboardButton(
                text='Соберите свой', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(text='О нас', callback_data=str('ABOUT_US')),
        ]
    ]
)

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
                callback_data=str('checkout'),
            ),
        ],
    ]


CATS = [
    'https://balthazar.club/uploads/posts/2022-10/thumbs/1666112702_2-balthazar-club-p-kotik-i-tortik-instagram-2.jpg',
    'https://balthazar.club/uploads/posts/2022-10/1666112669_4-balthazar-club-p-kotik-i-tortik-instagram-5.jpg',
    'https://balthazar.club/uploads/posts/2022-10/thumbs/1666112743_10-balthazar-club-p-kotik-i-tortik-instagram-11.jpg',
    'https://naurok-test2.nyc3.digitaloceanspaces.com/uploads/test/3652012/1691133/451133_1664952313.jpg',
    'https://animals.pibig.info/uploads/posts/2023-03/thumbs/1680263032_animals-pibig-info-p-kotenok-shipit-zhivotnie-instagram-1.jpg',
]

LOGO = 'https://www.ilovecake.ru/data/images/designer-cake.png'

CAT_CHEF = 'https://i.etsystatic.com/24476074/c/1993/1584/0/119/il/08ada3/2795064440/il_680x540.2795064440_cc73.jpg'

def send_cat(update):
    cat = choice(CATS)
    update.message.reply_photo(cat)
