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

from .buttons import MAIN_LAYOUT, WELCOME_TEXT, CUSTOMIZATION_LAYOUT

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
    keyboard = InlineKeyboardMarkup(MAIN_LAYOUT)

    if context.user_data.get('START_OVER'):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=WELCOME_TEXT,
            reply_markup=keyboard,
        )
    else:
        bold_entity = MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=29
        )
        update.message.reply_photo(
            'https://www.ilovecake.ru/data/images/designer-cake.png',
            caption=WELCOME_TEXT,
            reply_markup=keyboard,
            caption_entities=[bold_entity],
        )

    context.user_data['START_OVER'] = False
    return 'SELECTING_SCENARIO'


def select_cake(update: Update, context: CallbackContext) -> str:
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

    return 'SELECTING_CAKE'


def create_custom_cake(update: Update, context: CallbackContext) -> str:
    pass


def about_us(update: Update, context: CallbackContext) -> str:
    about_us_info = AboutUs.objects.first()

    buttons = [
        [
            InlineKeyboardButton(text='Назад', callback_data=str('MAIN')),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_caption(
        str(about_us_info), reply_markup=keyboard
    )


def go_main(update: Update, context: CallbackContext) -> str:
    keyboard = InlineKeyboardMarkup(MAIN_LAYOUT)
    bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=0, length=29)
    update.callback_query.edit_message_caption(
        WELCOME_TEXT, reply_markup=keyboard, caption_entities=[bold_entity]
    )


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_photo(
        'https://animals.pibig.info/uploads/posts/2023-03/thumbs/1680263032_animals-pibig-info-p-kotenok-shipit-zhivotnie-instagram-1.jpg'
    )

    return -1


def add_customizations(update: Update, context: CallbackContext) -> str:
    # say great choice, add choice to user data, offer customization
    user_choice = update.callback_query.data.split()
    if len(user_choice) == 2:
        _, cake_pk = user_choice

        cake = Cake.objects.get(pk=cake_pk)
        cake_repr = CakeRepresentation(cake)
        context.user_data['cake_repr'] = cake_repr
    else:
        cake_repr = context.user_data['cake_repr']
        cake = cake_repr.cake

    bold_entity = MessageEntity(
        type=MessageEntity.BOLD, offset=0, length=len(cake.title)
    )

    keyboard = InlineKeyboardMarkup(CUSTOMIZATION_LAYOUT)
    # update.callback_query.message.edit_caption(str(cake_repr), caption_entities=[bold_entity], reply_markup=keyboard)
    update.callback_query.message.reply_photo(
        cake.image_link,
        str(cake_repr),
        caption_entities=[bold_entity],
        reply_markup=keyboard,
    )

    return 'SELECTING_CUSTOMIZATIONS_TYPE'


def add_berries(update: Update, context: CallbackContext) -> str:
    buttons_row = [
        InlineKeyboardButton(
            text=berry.title, callback_data=str(f'add berries {berry.slug}')
        )
        for berry in Berry.objects.all()
    ]
    buttons = [
        buttons_row,
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_reply_markup(keyboard)

    return 'SELECTING_INGREDIENT'


def add_decor(update: Update, context: CallbackContext) -> str:
    buttons = [
        [
            InlineKeyboardButton(
                text=decor.title, callback_data=str(f'add decor {decor.slug}')
            )
        ]
        for decor in Decor.objects.all()
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_reply_markup(keyboard)

    return 'SELECTING_INGREDIENT'


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
    keyboard = InlineKeyboardMarkup(CUSTOMIZATION_LAYOUT)
    update.message.reply_photo(
        cake_repr.cake.image_link,
        str(cake_repr),
        caption_entities=[bold_entity],
        reply_markup=keyboard,
    )

    return 'SELECTING_CUSTOMIZATIONS_TYPE'


def add_ingredient(update: Update, context: CallbackContext) -> str:
    _, feature, ingredient = update.callback_query.data.split()

    if feature == 'berries':
        obj = Berry.objects.get(slug=ingredient)
    if feature == 'decor':
        obj = Decor.objects.get(slug=ingredient)

    cake_repr = context.user_data['cake_repr']
    features_list = getattr(cake_repr, feature)
    features_list.append(obj)

    # keyboard = InlineKeyboardMarkup(CUSTOMIZATION_LAYOUT)
    # update.callback_query.message.edit_caption(
    #     str(cake_repr), reply_markup=keyboard
    # )

    return add_customizations(update, context)


def go_to_check_out(update: Update, context: CallbackContext) -> str:
    cake_repr = context.user_data['cake_repr']
    update.callback_query.message.reply_photo(
        cake_repr.cake.image_link, str(cake_repr)
    )
    buttons = [
        [
            InlineKeyboardButton(text='Принять', callback_data=str('ACCEPT')),
        ],
        [
            InlineKeyboardButton(text='Отказаться', callback_data=str('-1')),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text(
        '⚠️ Продолжая, Вы соглашаетсь на обработку персональных данных',
        reply_markup=keyboard,
    )


def submit_accept(update: Update, context: CallbackContext) -> str:
    delivery_guy = 'https://xn----jtbnbixdby0fq.xn--p1ai/pics/5.png'
    update.callback_query.message.reply_photo(delivery_guy)


def stop_nested(update: Update, context: CallbackContext) -> str:
    """Completely end conversation from within nested conversation."""
    update.message.reply_text('Okay, bye.')

    return 'STOPPING'


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    customization_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_customizations, pattern='^complete')],
        states={
            'SELECTING_CUSTOMIZATIONS_TYPE': [
                CallbackQueryHandler(add_berries, pattern='^berries$'),
                CallbackQueryHandler(add_decor, pattern='^decor$'),
                CallbackQueryHandler(make_signature, pattern='^signature$'),

                CallbackQueryHandler(go_to_check_out, pattern='^check_out$'),
                CallbackQueryHandler(submit_accept, pattern='^ACCEPT$'),
            ],
            'SELECTING_INGREDIENT': [
                CallbackQueryHandler(add_ingredient, pattern='^add'),
            ],
            'TYPING': [MessageHandler(Filters.text, add_signature)],
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            'STOPPING': -1,
        },
    )

    # top level conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            'SELECTING_SCENARIO': [
                CallbackQueryHandler(
                    select_cake, pattern='^COMPLETE_CAKE$'
                ),
                CallbackQueryHandler(
                    create_custom_cake, pattern='^CUSTOM_CAKE$'
                ),
                CallbackQueryHandler(about_us, pattern='^ABOUT_US$'),
                CallbackQueryHandler(go_main, pattern='^MAIN$'),
            ],
            'CHECK_OUT': [],
            'SELECTING_CAKE': [customization_handler],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
