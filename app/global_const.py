from enum import Enum

from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME
)


class WebActions(Enum):
    SUBSCRIBE = 1
    PROMOTION = 2
    PAID = 3


UkassaPaymentStatus = {
    'pending': 1,
    'succeeded': 2,
    'waiting_for_capture': 3,
    'canceled': 4,
}

