from telegram import Update, MessageEntity, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from .buttons import MAIN_LAYOUT, WELCOME_TEXT
from ...models import Cake, AboutUs


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


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    send_cat(update)

    return -1



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

