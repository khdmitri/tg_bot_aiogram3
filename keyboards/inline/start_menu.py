from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from crud import crud_practise, crud_invoice
from db.session import SessionLocalAsync
from lexicon.lexicon_ru import LEXICON_MENU_RU, LEXICON_INLINE_MENU_RU, LEXICON_INLINE_ADMIN_MENU_RU, \
    LEXICON_CHAPTER_EXIT_RU, LEXICON_BUY_INLINE_MENU_RU
from models.practise import Practise


class StartMenuKeyboard:

    def __init__(self, online_practise_id: int, is_admin: bool = False):

        self.buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback + str(online_practise_id) if callback.startswith('view_practise:') else callback
            )
            for callback, description in LEXICON_INLINE_MENU_RU.items()
        ]

        self.nav_buttons = [
            InlineKeyboardButton(
                text=LEXICON_CHAPTER_EXIT_RU['about_exit'],
                callback_data='about_exit'
            )
        ]

        if is_admin:
            self.buttons += [
                InlineKeyboardButton(
                    text=description,
                    callback_data=callback
                )
                for callback, description in LEXICON_INLINE_ADMIN_MENU_RU.items()
            ]

        kb_nav_builder = InlineKeyboardBuilder()
        self.nav_keyboard = kb_nav_builder.row(*self.nav_buttons, width=1)

    def get_keyboard(self):
        kb_builder = InlineKeyboardBuilder()
        keyboard = kb_builder.row(*self.buttons, width=1)
        return keyboard.as_markup()

    def get_nav_keyboard(self):
        return self.nav_keyboard.as_markup()


async def _get_online_practise_id():
    online_practise_id = 0
    async with SessionLocalAsync() as db:
        online_practise: Practise = await crud_practise.get_online_practise(db)
        if online_practise:
            online_practise_id = online_practise.id

    return online_practise_id


async def get_start_menu_keyboard(user_id: int, is_admin: bool = False):
    instance = StartMenuKeyboard(online_practise_id=await _get_online_practise_id(), is_admin=is_admin)
    async with SessionLocalAsync() as db:
        valid_invoice = await crud_invoice.get_valid_online_invoice(db, user_id=user_id)
        if not valid_invoice:
            instance.buttons += [
                InlineKeyboardButton(
                    text=description,
                    callback_data=callback
                )
                for callback, description in LEXICON_BUY_INLINE_MENU_RU.items()
            ]
    return instance.get_keyboard()


async def get_nav_keyboard(is_admin: bool = False):
    instance = StartMenuKeyboard(online_practise_id=await _get_online_practise_id(), is_admin=is_admin)
    return instance.get_nav_keyboard()
