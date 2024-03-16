from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from app.global_const import WebActions
from app.utils import send_greeting_email, send_promotion_email
from crud import crud_web_user
from schemas import WebUserCreate
from utils.constants import WEBAPP_ACTIONS
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.post("/email", response_model=schemas.Msg)
async def process_email(
        db: AsyncSession = Depends(deps.get_db_async),
        *,
        data: schemas.WebEmailData
) -> Any:
    """
    Processing web user email
    """
    web_user = await crud_web_user.get_by_email(db, data.email)
    if not web_user:
        # Create new web user and send greeting email
        new_web_user = WebUserCreate(email=data.email)
        new_web_user = await crud_web_user.create(db, obj_in=new_web_user)

        if not new_web_user:
            raise HTTPException(
                status_code=403,
                detail="New user was not created",
            )
        else:
            send_greeting_email(new_web_user.email)

    match data.action:
        case WebActions.PROMOTION.value:
            send_promotion_email(data.email)

    return {"msg": "User was processed successfully"}
