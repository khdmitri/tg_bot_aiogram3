from aiogram import Router, F
from aiogram.filters import StateFilter, or_f

from filters import ChatTypeFilter
from filters.admin import IsAdminFilter
from lexicon.lexicon_ru import LEXICON_BTN_LABELS_RU
from states.admin import PractiseMenu, MediaMenu, Page
from states.group import GroupMenu
from . import practise as practise, media, post, group


def prepare_router() -> Router:
    admin_router = Router()
    admin_router.message.filter(ChatTypeFilter("private"))
    admin_router.callback_query.filter(IsAdminFilter())

    # ============= GROUP handlers ============

    admin_router.callback_query.register(group.show_online_lessons, F.data.in_({'show_online_lessons'}))
    admin_router.callback_query.register(group.view_online_lesson, F.data.startswith('online_lesson:'),
                                         StateFilter(GroupMenu.view_lessons))
    admin_router.callback_query.register(group.send_group_message, F.data.in_({'send_group_message'}),
                                         StateFilter(GroupMenu.view_group))
    admin_router.message.register(group.group_send_message_save,
                                  StateFilter(GroupMenu.group_message_prompt),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))

    # ============= END of GROUP handlers =====

    # ============= POST handlers ============

    admin_router.callback_query.register(post.manage_page, F.data.startswith('manage_page:'))
    admin_router.callback_query.register(post.add_post,
                                         F.data.in_({'add_post'}),
                                         StateFilter(Page.manage))
    admin_router.callback_query.register(post.edit_post,
                                         F.data.startswith('post:'),
                                         StateFilter(Page.manage))
    admin_router.callback_query.register(post.post_change_name_prompt,
                                         F.data.in_({'post_change_name'}),
                                         StateFilter(Page.edit))
    admin_router.callback_query.register(post.post_change_order_prompt,
                                         F.data.in_({'post_change_order'}),
                                         StateFilter(Page.edit))
    admin_router.callback_query.register(post.post_change_post_prompt,
                                         F.data.in_({'post_change_post'}),
                                         StateFilter(Page.edit))
    admin_router.message.register(post.post_change_name_save,
                                  StateFilter(Page.change_name),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(post.post_change_order_save,
                                  StateFilter(Page.change_order),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(post.post_change_post_save,
                                  StateFilter(Page.change_post),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(post.cancel_change, F.text == LEXICON_BTN_LABELS_RU['cancel_edit'],
                                  or_f(StateFilter(Page.change_name),
                                       StateFilter(Page.change_order),
                                       StateFilter(Page.change_post))
                                  )
    admin_router.callback_query.register(post.delete_post,
                                         F.data.in_({'delete_post'}),
                                         StateFilter(Page.edit))

    # ============= END of post handlers =====

    admin_router.callback_query.register(practise.manage_practises, F.data.in_({'manage_practises'}))
    admin_router.callback_query.register(practise.add_practise,
                                         F.data.in_({'add_practise'}),
                                         StateFilter(PractiseMenu.home))
    admin_router.callback_query.register(media.add_media,
                                         F.data.in_({'add_media'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(practise.edit_practise,
                                         F.data.startswith('practise:'))
    admin_router.callback_query.register(media.edit_media,
                                         F.data.startswith('lesson:'),
                                         or_f(StateFilter(PractiseMenu.edit), StateFilter(MediaMenu.edit)))
    admin_router.callback_query.register(media.edit_online_media,
                                         F.data.startswith('online_lesson:'),
                                         or_f(StateFilter(PractiseMenu.edit), StateFilter(MediaMenu.edit)))
    admin_router.callback_query.register(practise.practise_change_title_prompt,
                                         F.data.in_({'practise_change_title'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(media.media_change_title_prompt,
                                         F.data.in_({'media_change_title'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(practise.delete_practise,
                                         F.data.in_({'delete_practise'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(media.delete_media,
                                         F.data.in_({'delete_media'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(practise.practise_change_category_prompt,
                                         F.data.in_({'practise_change_category'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.message.register(practise.practise_change_title_save,
                                  StateFilter(PractiseMenu.change_title),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_title_save,
                                  StateFilter(MediaMenu.change_title),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.callback_query.register(practise.practise_change_description_prompt,
                                         F.data.in_({'practise_change_description'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(media.media_change_description_prompt,
                                         F.data.in_({'media_change_description'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(practise.practise_change_publish_prompt,
                                         F.data.in_({'practise_change_publish'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(media.media_change_free_prompt,
                                         F.data.in_({'media_change_free'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(media.media_change_stream_link_prompt,
                                         F.data.in_({'media_change_stream_link'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(media.media_change_action_date_prompt,
                                         F.data.in_({'media_change_action_date'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(media.spam_stream_link,
                                         F.data.in_({'spam_stream_link'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.message.register(practise.practise_change_description_save,
                                  StateFilter(PractiseMenu.change_description),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(practise.practise_change_category_save,
                                  StateFilter(PractiseMenu.change_category),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_description_save,
                                  StateFilter(MediaMenu.change_description),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_action_date_save,
                                  StateFilter(MediaMenu.change_action_date),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_stream_link_save,
                                  StateFilter(MediaMenu.change_stream_link),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.callback_query.register(practise.practise_change_media_prompt,
                                         F.data.in_({'practise_change_media'}),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(media.media_change_media_prompt,
                                         F.data.in_({'media_change_media'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(media.media_change_cost_prompt,
                                         F.data.in_({'media_change_cost'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(media.media_change_category_prompt,
                                         F.data.in_({'media_change_category'}),
                                         StateFilter(MediaMenu.edit))
    admin_router.callback_query.register(media.media_lessons_swap,
                                         F.data.startswith('lesson_swap:'),
                                         StateFilter(PractiseMenu.edit))
    admin_router.callback_query.register(practise.practise_lessons_swap,
                                         F.data.startswith('practise_swap:'),
                                         StateFilter(PractiseMenu.home))
    admin_router.message.register(practise.practise_change_media_save,
                                  StateFilter(PractiseMenu.change_media),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_media_save,
                                  StateFilter(MediaMenu.change_media),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_cost_save,
                                  StateFilter(MediaMenu.change_cost),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(media.media_change_category_save,
                                  StateFilter(MediaMenu.change_category),
                                  ~F.text.in_({LEXICON_BTN_LABELS_RU['cancel_edit']}))
    admin_router.message.register(practise.cancel_change, F.text == LEXICON_BTN_LABELS_RU['cancel_edit'],
                                  or_f(StateFilter(PractiseMenu.change_title),
                                       StateFilter(PractiseMenu.change_description),
                                       StateFilter(PractiseMenu.change_media),
                                       StateFilter(MediaMenu.change_category))
                                  )
    admin_router.message.register(media.cancel_change, F.text == LEXICON_BTN_LABELS_RU['cancel_edit'],
                                  or_f(StateFilter(MediaMenu.change_title),
                                       StateFilter(MediaMenu.change_description),
                                       StateFilter(MediaMenu.change_media),
                                       StateFilter(MediaMenu.change_cost))
                                  )

    return admin_router
