import os
import traceback
from pathlib import Path
from typing import Union

from aiogram import types

from app.definitions import ROOT_DIR
from crud import crud_blog
from db.session import SessionLocalAsync
from schemas import BlogCreate, BlogUpdate
from utils.constants import MessageTypes
from utils.logger import get_logger

logger = get_logger()

CHANNEL_ID = -1002060318202


async def check_new_post(msg: types.Message):
    if not msg.audio and not msg.video:
        orig_text = msg.caption if msg.caption else msg.text
        post_text = ""
        post_title = ""
        if orig_text:
            text = orig_text.split("\n")
            if isinstance(text, list):
                post_title = text[0]
                if len(post_title) > 128:
                    post_title = post_title[:128] + "..."
                post_text = "#nl#".join(text[1:])

        async with SessionLocalAsync() as db:
            new_post = await crud_blog.create(db, obj_in=BlogCreate(title=post_title, text=post_text, media_type=0))
            if new_post:
                if isinstance(msg.photo, list):
                    file_id = msg.photo[-1].file_id
                    file = await msg.bot.get_file(file_id)
                    file_path = file.file_path
                    file_name = file_path.split("/")[-1]
                    logger.info(file_name)
                    logger.info(file_path)
                    save_file_path = os.path.join(ROOT_DIR, "media/blog", str(new_post.id))
                    Path(save_file_path).mkdir(parents=True, exist_ok=True)
                    try:
                        await msg.bot.download_file(file_path, os.path.join(ROOT_DIR, os.path.join(save_file_path, file_name)))
                        await crud_blog.update(db, db_obj=new_post, obj_in=BlogUpdate(
                            id=new_post.id, media_type=MessageTypes.PHOTO.value, media_path=file_name
                        ))
                    except Exception as e:
                        logger.error(traceback.format_exc())
