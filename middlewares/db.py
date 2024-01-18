import datetime
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, Update, CallbackQuery

from crud import crud_user
from db.session import get_db_async, get_new_session, SessionLocalAsync
from schemas.user import UserUpdate, UserCreate


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        if "user" in data.keys():
            return await handler(event, data)

        if event.callback_query is not None:
            obj = event.callback_query
        elif event.message is not None:
            obj = event.message
        else:
            return await handler(event, data)

        async with SessionLocalAsync() as db:
            user = await crud_user.get_by_tg_id(db, obj.from_user.id)

            if user:
                updated_user = UserUpdate(id=user.id, last_visit=datetime.datetime.now())
                user = await crud_user.update(db, db_obj=user, obj_in=updated_user)
                data["user"] = user.as_dict()
            else:
                new_user = UserCreate(username=obj.from_user.username,
                                      tg_id=obj.from_user.id,
                                      fullname=obj.from_user.full_name,
                                      last_visit=datetime.datetime.now(),
                                      is_active=True,
                                      is_admin=False)
                user = await crud_user.create(db, obj_in=new_user)
                if user:
                    data["user"] = user.as_dict()

        return await handler(event, data)
