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

from .cake_representation import CakeRepresentation
from .buttons import CUSTOMIZATION_LAYOUT, send_cat
from .root_handler_callbacks import (
    start,
    stop,
    select_cake,
    create_custom_cake,
    about_us,
    go_main,
)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ...models import Cake, Berry, Decor


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


def add_customizations(update: Update, context: CallbackContext, came_from=None) -> str:
    # if callback_query and 3 - after adding ingredient
    # if callback_query and 2 = after selecting complete cake
    # if not callback_query - after typing
    keyboard = InlineKeyboardMarkup(CUSTOMIZATION_LAYOUT)

    if update.callback_query:
        user_choice = update.callback_query.data.split()
        if len(user_choice) == 2:
            # I need new message here
            _, cake_pk = user_choice

            cake = Cake.objects.get(pk=cake_pk)
            cake_repr = CakeRepresentation(cake)
            context.user_data['cake_repr'] = cake_repr
            update.callback_query.message.reply_photo(
                cake.image_link,
                str(cake_repr),
                caption_entities=[cake_repr.bold_entity],
                reply_markup=keyboard,
            )
        elif came_from == 'disagree':
            cake_repr = context.user_data['cake_repr']
            cake = cake_repr.cake
            update.callback_query.message.reply_photo(
                cake.image_link,
                str(cake_repr),
                caption_entities=[cake_repr.bold_entity],
                reply_markup=keyboard,
            )
        else:
            # I need edit message here
            cake_repr = context.user_data['cake_repr']
            update.callback_query.message.edit_caption(
                str(cake_repr),
                caption_entities=[cake_repr.bold_entity],
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
        'Мы можем разместить на торте любую надпись.\nНапример: «С днем рождения!»'
    )
    update.callback_query.message.reply_text('Введите желаемую надпись:')

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


def ask_for_terms_agreement(update: Update, context: CallbackContext) -> str:
    cake_repr = context.user_data['cake_repr']
    update.callback_query.message.edit_reply_markup()
    buttons = [
        [
            InlineKeyboardButton(text='Принять', callback_data='agree'),
        ],
        [
            InlineKeyboardButton(text='Отказаться', callback_data='disagree'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    asd = MessageEntity(MessageEntity.TEXT_LINK, offset=17, length=12, url='https://kpmg.com/kz/ru/home/misc/personal-data.html')
    update.callback_query.message.reply_text(
        '⚠️ Продолжая, Вы соглашаетесь на обработку персональных данных.',
        reply_markup=keyboard,
        entities=[asd]
    )

    return 'ACCEPTING_TERMS'


def select_shipping(update: Update, context: CallbackContext) -> str:
    delivery_guy = 'https://xn----jtbnbixdby0fq.xn--p1ai/pics/5.png'
    update.callback_query.message.reply_photo(delivery_guy)
    # buttons for shipping

    return 'SELECTING_SHIPPING'


def return_to_customization(update: Update, context: CallbackContext) -> str:
    update.callback_query.message.reply_text('К сожалению мы не можем оформить заказ без Вашего разрешения :(')

    return add_customizations(update, context, 'disagree')




def stop_nested(update: Update, context: CallbackContext) -> str:
    """Completely end conversation from within nested conversation."""
    send_cat(update)

    return 'STOPPING'


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    shipping_handler = []

    customization_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_customizations, pattern='^complete')
        ],
        states={
            'SELECTING_CUSTOMIZATIONS_TYPE': [
                CallbackQueryHandler(add_berries, pattern='^berries$'),
                CallbackQueryHandler(add_decor, pattern='^decor$'),
                CallbackQueryHandler(make_signature, pattern='^signature$'),
                CallbackQueryHandler(
                    ask_for_terms_agreement, pattern='^checkout$'
                ),
            ],
            'SELECTING_INGREDIENT': [
                CallbackQueryHandler(add_ingredient, pattern='^add'),
            ],
            'TYPING': [MessageHandler(Filters.text, add_signature)],
            'ACCEPTING_TERMS': [
                CallbackQueryHandler(select_shipping, pattern='^agree'),
                CallbackQueryHandler(return_to_customization, pattern='^disagree')
            ],
            'SELECTING_SHIPPING': [shipping_handler],
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
                CallbackQueryHandler(select_cake, pattern='^COMPLETE_CAKE$'),
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
