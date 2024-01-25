from aiogram import Router, F
from aiogram.enums import ContentType

from handlers.payment import payment


def prepare_router() -> Router:
    payment_router = Router()

    payment_router.pre_checkout_query.register(payment.pre_checkout_query)
    payment_router.message.register(payment.successful_payment, F.content_type == ContentType.SUCCESSFUL_PAYMENT)

    return payment_router
