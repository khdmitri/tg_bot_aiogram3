from typing import List, Any

from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, SentWebAppMessage
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from crud import crud_practise
from schemas import Practise
from utils.bot_instance import BotInstanceSingleton

router = APIRouter()


@router.get("/", response_model=List[schemas.Practise])
async def read_practises(
    db: AsyncSession = Depends(deps.get_db_async),
    skip: int = 0,
    limit: int = 100,
) -> List[Practise]:
    """
    Retrieve practises.
    """
    practises = await crud_practise.get_practises_by_order(db, only_published=True, include_online=False)
    return practises


@router.post("/webapp_data")
async def webapp_data_action(
        *,
        db: AsyncSession = Depends(deps.get_db_async),
        data: schemas.WebAppData
) -> Any:
    """
    Process webapp_data.
    """
    bot_instance = BotInstanceSingleton().get_instance()
    # message = InputTextMessageContent(message_text="Это основное тело сообщения", parse_mode="html")
    # answer = InlineQueryResultArticle(type="article",
    #                                   id=":".join([str(data.user_id), str(data.action), str(data.order_id)]),
    #                                   title="Вы заказали оплату, она сейчас будет произведена",
    #                                   input_message_content=message)
    # result: SentWebAppMessage = await bot_instance.answer_web_app_query(data.query_id, answer)
    result = await bot_instance.send_message(data.user_id,
                                             text=f"Data received: {data.action}:{data.user_id}:{data.order_id}")
    print("RESULT:", result)
