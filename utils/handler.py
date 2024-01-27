from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import Message, InputMediaPhoto, InputMediaVideo
from sqlalchemy.ext.asyncio import AsyncSession

from crud import crud_media_group, crud_post, crud_group
from db.session import SessionLocalAsync
from middlewares import message_logger
from models.post import Post
from utils import log_message, text_decorator
from utils.constants import MessageTypes


async def if_user_is_group_member(db: AsyncSession, *, user_id, media_id):
    member = await crud_group.is_member(db, user_id=user_id, media_id=media_id)
    if member:
        return True
    else:
        return False


async def prepare_context(state: FSMContext, new_state: State, message: Message):
    # Изменяем состояние
    await state.set_state(new_state)
    # Чистим контент прошлого состояния
    await message_logger.log_message.clean_content(message.chat.id, message)


async def prepare_media_group(media_group_id: int):
    result = []
    async with SessionLocalAsync() as db:
        group_db = await crud_media_group.get_multi_by_media_group_id(db, media_group_id)
        for media in group_db:
            match media.media_type:
                case MessageTypes.PHOTO.value:
                    result.append(InputMediaPhoto(media=media.media_file_id))
                case MessageTypes.VIDEO.value:
                    result.append(InputMediaVideo(media=media.media_file_id))

    return result


async def show_post(message: Message, post: Post):
    message_type: int = post.message_type
    match message_type:
        case MessageTypes.VIDEO.value:
            await log_message.add_message(await message.answer_video(video=post.media_file_id))
        case MessageTypes.PHOTO.value:
            await log_message.add_message(await message.answer_photo(photo=post.media_file_id))
        case MessageTypes.MEDIA_GROUP.value:
            await log_message.add_message(await message.answer_media_group(
                media=await prepare_media_group(post.media_group_id)))
        case MessageTypes.TEXT_MESSAGE.value:
            await log_message.add_message(await message.answer(text=text_decorator.not_empty(post.text)))


async def show_page(*, message: Message, page):
    async with SessionLocalAsync() as db:
        posts = await crud_post.get_posts_by_page(db, page)
        for post in posts:
            await show_post(message, post)
