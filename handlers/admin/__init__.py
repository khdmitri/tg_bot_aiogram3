from aiogram import Router, F
from aiogram.filters import StateFilter, or_f

from filters import ChatTypeFilter
from filters.admin import IsAdminFilter
from lexicon.lexicon_ru import LEXICON_BTN_LABELS_RU
from states.admin import PractiseMenu
from . import practise as practise


def prepare_router() -> Router:
    admin_router = Router()
    admin_router.message.filter(ChatTypeFilter("private"))
    admin_router.callback_query.filter(IsAdminFilter())

    admin_router.callback_query.register(practise.manage_practises, F.data.in_({'manage_practises'}))
    admin_router.callback_query.register(practise.add_practise,
                                         F.data.in_({'add_practise'}),
                                         StateFilter(PractiseMenu.home))
    admin_router.callback_query.register(practise.edit_practise,
                                         F.data.startswith('practise:'),
                                         StateFilter(PractiseMenu.home))
    admin_router.callback_query.register(practise.practise_change_title_prompt,
                                         F.data.in_({'practise_change_title'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(practise.delete_practise,
                                         F.data.in_({'delete_practise'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.message.register(practise.practise_change_title_save,
                                  StateFilter(PractiseMenu.change_title),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.callback_query.register(practise.practise_change_description_prompt,
                                         F.data.in_({'practise_change_description'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.message.register(practise.practise_change_description_save,
                                  StateFilter(PractiseMenu.change_description),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.callback_query.register(practise.practise_change_media_prompt,
                                         F.data.in_({'practise_change_media'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.message.register(practise.practise_change_media_save,
                                  StateFilter(PractiseMenu.change_media),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(practise.cancel_change, F.text == LEXICON_BTN_LABELS_RU['cancel_edit'],
                                  or_f(StateFilter(PractiseMenu.change_title),
                                       StateFilter(PractiseMenu.change_description))
                                  )

    return admin_router
