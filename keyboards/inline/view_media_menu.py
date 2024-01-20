from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from lexicon.lexicon_ru import LEXICON_INLINE_VIEW_MEDIA_NAV_MENU


class MediaMenuKeyboard:

    def __init__(self, practise_id):
        self.practise_id = practise_id

        self.nav_buttons = [
            InlineKeyboardButton(
                text=description,
                callback_data=callback if callback != 'view_practise:' else callback + str(self.practise_id)
            )
            for callback, description in LEXICON_INLINE_VIEW_MEDIA_NAV_MENU.items()
        ]

    def get_back_previous(self):
        kb_builder = InlineKeyboardBuilder()
        return kb_builder.row(*self.nav_buttons, width=1).as_markup()
