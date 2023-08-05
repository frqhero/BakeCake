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
from .buttons import CUSTOMIZATION_LAYOUT, send_cat, CAT_CHEF
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


def add_customizations(update: Update, context: CallbackContext) -> str:
    # if callback_query and 3 - after adding ingredient
    # if callback_query and 2 = after selecting complete cake
    # if not callback_query - after typing
    update.callback_query.answer()
    keyboard = InlineKeyboardMarkup(CUSTOMIZATION_LAYOUT)

    user_choice = update.callback_query.data.split()
    if len(user_choice) == 2:
        # I need new message here
        _, cake_pk = user_choice
        cake = Cake.objects.get(pk=cake_pk)
        cake_repr = CakeRepresentation(cake)
        context.user_data['cake_repr'] = cake_repr
        update.callback_query.message.reply_photo(
            cake_repr.cake.image_link,
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
                text=decor.title, callback_data=str(f'add decors {decor.slug}')
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
        cake_repr.signature = signature

    keyboard = InlineKeyboardMarkup(CUSTOMIZATION_LAYOUT)
    update.message.reply_photo(
        cake_repr.cake.image_link,
        str(cake_repr),
        caption_entities=[cake_repr.bold_entity],
        reply_markup=keyboard,
    )

    return 'SELECTING_CUSTOMIZATIONS_TYPE'


def add_ingredient(update: Update, context: CallbackContext) -> str:
    _, feature, ingredient = update.callback_query.data.split()

    if feature == 'berries':
        ingredient_obj = Berry.objects.get(slug=ingredient)
    if feature == 'decors':
        ingredient_obj = Decor.objects.get(slug=ingredient)

    cake_repr = context.user_data['cake_repr']

    features_list = getattr(cake_repr, feature)
    features_list.add(ingredient_obj)

    return add_customizations(update, context)


def ask_for_terms_agreement(update: Update, context: CallbackContext) -> str:
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
    url = MessageEntity(
        MessageEntity.TEXT_LINK,
        offset=17,
        length=12,
        url='https://kpmg.com/kz/ru/home/misc/personal-data.html',
    )
    update.callback_query.message.reply_text(
        '⚠️ Продолжая, Вы соглашаетесь на обработку персональных данных.',
        reply_markup=keyboard,
        entities=[url],
    )

    return 'ACCEPTING_TERMS'


def select_shipping(update: Update, context: CallbackContext) -> str:
    delivery_guy = 'https://xn----jtbnbixdby0fq.xn--p1ai/pics/5.png'
    # buttons for shipping
    buttons = [
        [
            InlineKeyboardButton(text='Доставка', callback_data='delivery'),
            InlineKeyboardButton(text='Самовывоз', callback_data='pickup'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_photo(
        delivery_guy, reply_markup=keyboard
    )

    return 'SELECTING_SHIPPING'


def return_to_start(update: Update, context: CallbackContext) -> str:
    update.callback_query.message.reply_text(
        'К сожалению мы не можем оформить заказ без Вашего разрешения :('
    )
    context.user_data['came_from'] = 'disagree'
    start(update, context)

    return 'DISAGREE'


def stop_nested(update: Update, context: CallbackContext) -> str:
    """Completely end conversation from within nested conversation."""
    send_cat(update)

    return 'STOPPING'


def ask_type_address(update: Update, context: CallbackContext) -> str:
    update.callback_query.answer()
    context.user_data['cake_repr'].delivery = True
    update.callback_query.message.reply_text(
        'Напишите пожалуйста адрес доставки'
    )

    return 'TYPING'


def select_timeslot(update: Update, context: CallbackContext) -> str:
    address = update.message.text
    cake_repr = context.user_data['cake_repr']
    cake_repr.address = address

    buttons = []
    for num, timeslot in Cake.TIMESLOTS:
        buttons.append([InlineKeyboardButton(timeslot, callback_data=num)])
    keyboard = InlineKeyboardMarkup(buttons)

    ready_at = str(context.user_data['cake_repr'].ready_at)

    update.message.reply_photo(
        CAT_CHEF,
        f'Ваш торт будет готов {ready_at} :) Выберите время получения',
        reply_markup=keyboard,
    )

    return 'DONE_SHIPPING'


def ask_for_comment(update: Update, context: CallbackContext) -> str:
    context.user_data['cake_repr'].timeslot = int(update.callback_query.data)
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Да', callback_data='yes'),
                InlineKeyboardButton('Нет', callback_data='no'),
            ]
        ]
    )
    update.callback_query.message.reply_text(
        'Отлично и напоследок, желаете оставить дополнительный комментарий к заказу?',
        reply_markup=keyboard,
    )

    return 'ADDING_COMMENT'


def ask_type_comment(update: Update, context: CallbackContext) -> str:
    update.callback_query.message.reply_text('Пожалуйста напишите чтобы вы хотели чтобы мы знали еще о вашем заказе?')

    return 'TYPING'


def send_order(update: Update, context: CallbackContext) -> str:
    update.callback_query.message.reply_text('sent')
    # show result and ask to submit
    return 'SENDING_ORDER'


def write_comment(update: Update, context: CallbackContext) -> str:
    send_order(update, context)

    return 'SENDING_ORDER'


def sum_up_n_send_order(update: Update, context: CallbackContext) -> str:
    # show result and ask to submit
    cake_repr = context.user_data['cake_repr']
    cake_repr.comment = update.message.text
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('Да', callback_data='yes'),
                InlineKeyboardButton('Нет', callback_data='no'),
            ]
        ]
    )
    update.message.reply_photo(
        cake_repr.cake.image_link,
        str(cake_repr),
    )
    update.message.reply_text(
        'Проверьте пожалуйста, если все верно, то мы готовы принять Ваш заказ',
        reply_markup=keyboard
    )

    return 'SENDING_ORDER'


def create_order(update: Update, context: CallbackContext) -> str:
    cake_repr = context.user_data['cake_repr']
    clients_cake = Cake()
    clients_cake.title = cake_repr.cake.title
    clients_cake.image_link = cake_repr.cake.image_link
    clients_cake.description = cake_repr.cake.description
    clients_cake.price = cake_repr.cake.price
    clients_cake.level = cake_repr.level
    clients_cake.shape = cake_repr.shape
    clients_cake.topping = cake_repr.topping
    clients_cake.signature = cake_repr.signature
    clients_cake.delivery = cake_repr.delivery
    clients_cake.ready_at = cake_repr.ready_at
    clients_cake.timeslot = cake_repr.timeslot
    clients_cake.address = cake_repr.address
    clients_cake.comment = cake_repr.comment
    clients_cake.save()
    # m2m after save
    if cake_repr.berries:
        for berry in cake_repr.berries:
            clients_cake.berries.add(berry)
    if cake_repr.decors:
        for decor in cake_repr.decors:
            clients_cake.decors.add(decor)


    update.callback_query.message.reply_text('Спасибо, заказ создан!')

    return 'ORDER_CREATED'


def main():
    tg_bot_token = settings.TG_BOT_TOKEN
    updater = Updater(token=tg_bot_token)
    dispatcher = updater.dispatcher

    timeslot_n_comment_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_for_comment, pattern='^\d$')],
        states={
            'ADDING_COMMENT': [
                CallbackQueryHandler(ask_type_comment, pattern='^yes$'),
                CallbackQueryHandler(send_order, pattern='^no$'),
            ],
            'TYPING': [MessageHandler(Filters.text, sum_up_n_send_order)],
            'SENDING_ORDER': [CallbackQueryHandler(create_order, pattern='^yes$')],
        },
        fallbacks={},
        map_to_parent={
            'ORDER_CREATED': -1
        }
    )

    shipping_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(select_shipping, pattern='^agree'),
            CallbackQueryHandler(return_to_start, pattern='^disagree'),
        ],
        states={
            'SELECTING_SHIPPING': [
                CallbackQueryHandler(ask_type_address, pattern='^delivery$')
            ],
            'SELECTING_TIMESLOT': [],
            'TYPING': [MessageHandler(Filters.text, select_timeslot)],
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            'DISAGREE': 'SELECTING_SCENARIO',
            'STOPPING': -1,
            'DONE_SHIPPING': 'SELECTING_TIMING',
        },
    )

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
        },
        fallbacks=[CommandHandler('stop', stop_nested)],
        map_to_parent={
            'STOPPING': -1,
            'ACCEPTING_TERMS': 'ACCEPTING_TERMS',
        },
    )

    # top level conversation handler
    root_handler = ConversationHandler(
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
            'SELECTING_CAKE': [customization_handler],
            'ACCEPTING_TERMS': [shipping_conv],
            'SELECTING_TIMING': [timeslot_n_comment_conv],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(root_handler)

    updater.start_polling()
    updater.idle()


class Command(BaseCommand):
    def handle(self, *args, **options):
        main()
