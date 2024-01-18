from typing import Any, Union, Dict, Optional

from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery

from crud import crud_user
from db.session import SessionLocalAsync
from models.user import User


class IsAdminFilter(Filter):
    async def __call__(self, msg: Message | CallbackQuery) -> Union[bool, Dict[str, Any]]:
        user_id = msg.from_user.id
        async with SessionLocalAsync() as db:
            user_db: Optional[User] = await crud_user.get_by_tg_id(db, tg_id=user_id)
            if user_db and user_db.tg_id == user_id:
                return True

        return False
