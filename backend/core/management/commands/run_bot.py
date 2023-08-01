from textwrap import dedent
import logging
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MessageEntity,
)
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ...models import Cake, Berry, Decor, AboutUs


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


class CakeRepresentation:
    def __init__(self, cake, berries=None, decor=None, signature=None):
        self.cake = cake
        if not berries:
            self.berries = []
        if not decor:
            self.decor = []
        if not signature:
            self.signature = []

    def add_signature(self, signature):
        self.signature.append(signature)

    def __str__(self):
        main_text = f'{self.cake.title}\n\n{self.cake.description}'
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


def start(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    title = 'Добро пожаловать в Bake Cake!'
    info = 'В нашем магазине вы можете выбрать готовый торт или собрать свой!'
    ending = 'Для завершения нажмите "Отменить" или наберите /stop'

    text = title + '\n\n' + info + '\n\n' + ending

    buttons = [
        [
            InlineKeyboardButton(
                text='Готовый', callback_data=str('COMPLETE_CAKE')
            ),
            InlineKeyboardButton(
                text='Соберите свой', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(text='О нас', callback_data=str('ABOUT_US')),
        ],
        [
            InlineKeyboardButton(text='Отменить', callback_data=str('-1')),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get('START_OVER'):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard,
        )
    else:
        bold_entity = MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=29
        )
        update.message.reply_photo(
            'https://www.ilovecake.ru/data/images/designer-cake.png',
            caption=text,
            reply_markup=keyboard,
            caption_entities=[bold_entity],
        )

    context.user_data['START_OVER'] = False
    return 'SELECT_CAKE_TYPE'


def show_complete_cakes(update: Update, context: CallbackContext) -> str:
    cakes = Cake.objects.all()

    for cake in cakes:
        bold_entity = MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=len(cake.title)
        )
        buttons = [
            [
                InlineKeyboardButton(
                    text='Выбрать', callback_data=str(f'complete {cake.pk}')
                ),
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        update.callback_query.message.reply_photo(
            cake.image_link,
            cake.title
            + '\n'
            + str(cake.price)
            + ' руб.'
            + '\n\n'
            + cake.description,
            caption_entities=[bold_entity],
            reply_markup=keyboard,
        )

    return 'CUSTOMIZATION'


def create_custom_cake(update: Update, context: CallbackContext) -> str:
    pass


def about_us(update: Update, context: CallbackContext) -> str:
    about_us_info = AboutUs.objects.first()

    buttons = [
        [
            InlineKeyboardButton(
                text='Готовый', callback_data=str('COMPLETE_CAKE')
            ),
            InlineKeyboardButton(
                text='Соберите свой', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(text='Главная', callback_data=str('MAIN')),
        ],
        [
            InlineKeyboardButton(text='Отменить', callback_data=str('-1')),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_caption(
        str(about_us_info), reply_markup=keyboard
    )


def go_main(update: Update, context: CallbackContext) -> str:
    title = 'Добро пожаловать в Bake Cake!'
    info = 'В нашем магазине вы можете выбрать готовый торт или собрать свой!'
    ending = 'Для завершения нажмите "Отменить" или наберите /stop'

    text = title + '\n\n' + info + '\n\n' + ending

    buttons = [
        [
            InlineKeyboardButton(
                text='Готовый', callback_data=str('COMPLETE_CAKE')
            ),
            InlineKeyboardButton(
                text='Соберите свой', callback_data=str('CUSTOM_CAKE')
            ),
            InlineKeyboardButton(text='О нас', callback_data=str('ABOUT_US')),
        ],
        [
            InlineKeyboardButton(text='Отменить', callback_data=str('-1')),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=0, length=29)
    update.callback_query.edit_message_caption(
        text, reply_markup=keyboard, caption_entities=[bold_entity]
    )


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_photo(
        'https://animals.pibig.info/uploads/posts/2023-03/thumbs/1680263032_animals-pibig-info-p-kotenok-shipit-zhivotnie-instagram-1.jpg'
    )

    return -1


def end(update: Update, context: CallbackContext) -> int:
    update.callback_query.answer('Удаляем беседу тогда...')
    update.callback_query.delete_message()

    return -1


def offer_custom(update: Update, context: CallbackContext) -> str:
    # say great choice, add choice to user data, offer customization
    _, cake_pk = update.callback_query.data.split()

    cake = Cake.objects.get(pk=cake_pk)
    cake_repr = CakeRepresentation(cake)
    context.user_data['cake_repr'] = cake_repr

    bold_entity = MessageEntity(
        type=MessageEntity.BOLD, offset=0, length=len(cake.title)
    )
    buttons = [
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
                text='Вернуться к выбору торта', callback_data=-1
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_photo(
        cake.image_link,
        str(cake_repr),
        caption_entities=[bold_entity],
        reply_markup=keyboard,
    )

    return 'SELECTING_FEATURES'


def add_berries(update: Update, context: CallbackContext) -> str:
    buttons_row = [
        InlineKeyboardButton(
            text=berry.title, callback_data=str(f'add berries {berry.slug}')
        )
        for berry in Berry.objects.all()
    ]
    buttons = [
        buttons_row,
        [
            InlineKeyboardButton(
                text='Вернуться к выбору торта', callback_data=-1
            ),
        ],
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_reply_markup(keyboard)


def add_decor(update: Update, context: CallbackContext) -> str:
    buttons_row = [
        [
            InlineKeyboardButton(
                text=decor.title, callback_data=str(f'add decor {decor.slug}')
            )
        ]
        for decor in Decor.objects.all()
    ]
    buttons_row.append(
        [
            InlineKeyboardButton(
                text='Вернуться к выбору торта', callback_data=-1
            ),
        ]
    )

    keyboard = InlineKeyboardMarkup(buttons_row)
    update.callback_query.edit_message_reply_markup(keyboard)


def make_signature(update: Update, context: CallbackContext) -> str:
    update.callback_query.edit_message_reply_markup()
    update.callback_query.message.reply_text(
        'Мы можем разместить на торте любую надпись, например: «С днем рождения!»\n'
        'Введите желаемую надпись:'
    )

    return 'TYPING'


def add_signature(update: Update, context: CallbackContext) -> str:
    signature = update.message.text
    cake_repr = context.user_data['cake_repr']
    if signature:
        cake_repr.add_signature(signature)

    bold_entity = MessageEntity(
        type=MessageEntity.BOLD, offset=0, length=len(cake_repr.cake.title)
    )
    buttons = [
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
                text='Вернуться к выбору торта', callback_data=-1
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_photo(
        cake_repr.cake.image_link,
        str(cake_repr),
        caption_entities=[bold_entity],
        reply_markup=keyboard,
    )

    return 'SELECTING_FEATURES'


def add_extra_ingredient(update: Update, context: CallbackContext) -> str:
    _, feature, ingredient = update.callback_query.data.split()

    if feature == 'berries':
        obj = Berry.objects.get(slug=ingredient)
    if feature == 'decor':
        obj = Decor.objects.get(slug=ingredient)

    cake_repr = context.user_data['cake_repr']
    features_list = getattr(cake_repr, feature)
    features_list.append(obj)

    buttons = [
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
                text='Вернуться к выбору торта', callback_data=-1
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.edit_caption(
        str(cake_repr), reply_markup=keyboard
    )

    return offer_custom(update, context)


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    customization_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(offer_custom, pattern='^complete')],
        states={
            'SELECTING_FEATURES': [
                CallbackQueryHandler(add_berries, pattern='^berries$'),
                CallbackQueryHandler(add_decor, pattern='^decor$'),
                CallbackQueryHandler(make_signature, pattern='^signature$'),
                CallbackQueryHandler(add_extra_ingredient, pattern='^add'),
                CallbackQueryHandler(end, pattern='^-1$'),
            ],
            'TYPING': [MessageHandler(Filters.text, add_signature)],
        },
        fallbacks=[],
        map_to_parent={-1: 'CUSTOMIZATION'},
    )

    # top level conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'SELECT_CAKE_TYPE': [
                CallbackQueryHandler(
                    show_complete_cakes, pattern='^COMPLETE_CAKE$'
                ),
                CallbackQueryHandler(
                    create_custom_cake, pattern='^CUSTOM_CAKE$'
                ),
                CallbackQueryHandler(about_us, pattern='^ABOUT_US$'),
                CallbackQueryHandler(go_main, pattern='^MAIN$'),
                CallbackQueryHandler(end, pattern='^-1$'),
            ],
            'CUSTOMIZATION': [customization_handler],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
