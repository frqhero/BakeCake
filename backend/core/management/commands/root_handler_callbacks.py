from telegram import (
    Update,
    MessageEntity,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext

from .buttons import MAIN_LAYOUT, WELCOME_TEXT, send_cat, LOGO
from ...models import Cake, AboutUs


def start(update: Update, context: CallbackContext) -> str:
    # send a message and then return select_cake_type
    bold_entity = MessageEntity(type=MessageEntity.BOLD, offset=0, length=29)
    came_from = context.user_data.get('came_from')
    if not came_from:
        update.message.reply_photo(
            LOGO,
            caption=WELCOME_TEXT,
            reply_markup=MAIN_LAYOUT,
            caption_entities=[bold_entity],
        )
    elif came_from == 'disagree':
        update.callback_query.answer()
        update.callback_query.message.reply_photo(
            LOGO,
            caption=WELCOME_TEXT,
            reply_markup=MAIN_LAYOUT,
            caption_entities=[bold_entity],
        )
    elif came_from == 'go_main':
        update.callback_query.answer()
        update.callback_query.edit_message_caption(
            WELCOME_TEXT,
            reply_markup=MAIN_LAYOUT,
            caption_entities=[bold_entity],
        )

    context.user_data['came_from'] = None
    return 'SELECTING_SCENARIO'


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    send_cat(update)

    return -1


def select_cake(update: Update, context: CallbackContext) -> str:
    update.callback_query.answer()

    cakes = Cake.objects.filter(status=6)

    for cake in cakes:
        bold_entity = MessageEntity(
            type=MessageEntity.BOLD, offset=0, length=len(cake.title)
        )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text='Выбрать',
                        callback_data=str(f'complete {cake.pk}'),
                    )
                ]
            ]
        )
        update.callback_query.message.reply_photo(
            cake.image_link,
            str(cake),
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
    context.user_data['came_from'] = 'go_main'
    start(update, context)
