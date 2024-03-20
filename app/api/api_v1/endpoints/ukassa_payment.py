import traceback
from typing import Any, Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from yookassa.domain.notification import WebhookNotification

import schemas
from app.api import deps
from app.global_const import UkassaPaymentStatus
from app.payment.ukassa import UkassaPayment
from app.utils.practise import get_practise_price
from app.utils_module import send_paid_email
from crud import crud_web_payment
from schemas import WebPayment, UkassaEventSchema
from schemas.webappdata import UkassaPaymentSchema
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.post("/create")
async def create_payment(
        *,
        data: schemas.WebCreatePaymentData
) -> UkassaPaymentSchema:
    payment_ukassa = UkassaPayment(email=data.email, practise_id=data.practise_id)
    _, price = await get_practise_price(practise_id=data.practise_id)
    payment = await payment_ukassa.create_payment(price)
    return payment


@router.get("/find_one/{order_id}", response_model=WebPayment)
async def find_one(
    order_id: str
) -> WebPayment:
    return await UkassaPayment.find_one(order_id)


@router.post("/event")
async def ukassa_event(
        request: Request,
        db: AsyncSession = Depends(deps.get_db_async),
):
    event_dict = request.json()
    try:
        notification_object = WebhookNotification(event_dict)
        obj = notification_object.object
        amount = 0
        if obj.get("amount", None) and obj["amount"].get("value", None):
            amount = int(obj["amount"]["value"])
        status = -1
        if obj.get("status", None):
            if obj["status"] in UkassaPaymentStatus.keys():
                status = UkassaPaymentStatus[obj["status"]]
        schema_obj = UkassaEventSchema(id=obj.get("id", None), amount=amount, status=status)
        payment = await crud_web_payment.get(db, id=schema_obj.id)
        if payment:
            if payment.status != UkassaPaymentStatus['succeeded'] and schema_obj.amount >= payment.amount:
                payment.status = schema_obj.status
                db.add(payment)
                await db.commit()
                await db.refresh(payment)
                if payment.status != UkassaPaymentStatus['succeeded']:
                    send_paid_email(
                        payment.web_user.email,
                        payment.practise.channel_web_link,
                        payment.practise.disk_resource_link
                    )
    except Exception:
        logger.error(traceback.format_exc())

    return Response(status_code=200)
