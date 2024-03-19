from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

import schemas
from app.api import deps
from app.payment.ukassa import UkassaPayment
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()


@router.post("/create")
async def create_payment(
        *,
        data: schemas.WebCreatePaymentData
) -> Any:
    payment_ukassa = UkassaPayment(email=data.email, practise_id=data.practise_id)
    return payment_ukassa.create_payment(data.amount)
