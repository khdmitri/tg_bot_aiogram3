from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from app.global_const import WebActions
from app.utils_module import send_greeting_email, send_promotion_email, get_program_table_values, send_program_email, \
    send_program_analysis_email
from core.sphere_config import SphereConfig
from crud import crud_web_user
from schemas import WebUserCreate, SphereWebUser
from schemas.webappdata import SphereWebUserEmail
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


@router.post("/prepare_practise")
async def prepare_practise(
        data: List[SphereWebUser]
) -> Any:
    sphere_config = SphereConfig(web_user_id=None, sphere_list=data)

    return await sphere_config.prepare_practise()


@router.post("/send_practise")
async def send_practise(
        db: AsyncSession = Depends(deps.get_db_async),
        *,
        data: SphereWebUserEmail
) -> Any:
    web_user = await crud_web_user.get_by_email_or_create(db, email=data.email)
    if web_user:
        sphere_config = SphereConfig(web_user_id=web_user.id, sphere_list=data.sphere_list)
        program = await sphere_config.prepare_practise()
        table_values = get_program_table_values(program)
        send_program_email(email_to=data.email, table_values=table_values)
        diff = await sphere_config.update_practise()
        if diff:
            send_program_analysis_email(email_to=data.email, table_values=diff)
    else:
        raise HTTPException(
            status_code=404,
            detail="User was not found",
        )
