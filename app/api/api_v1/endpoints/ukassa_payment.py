from typing import Any, Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from app.payment.ukassa import UkassaPayment
from app.utils.practise import get_practise_price
from schemas import WebPayment
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.post("/create")
async def create_payment(
        *,
        data: schemas.WebCreatePaymentData
) -> Any:
    payment_ukassa = UkassaPayment(email=data.email, practise_id=data.practise_id)
    _, price = get_practise_price(practise_id=data.practise_id)
    payment = await payment_ukassa.create_payment(price)
    return payment


@router.get("/find_one/{order_id}")
async def find_one(
    order_id: str
) -> WebPayment:
    return await UkassaPayment.find_one(order_id)
