import uuid

from yookassa import Payment, Configuration

from app.core.config import settings
from app.global_const import UkassaPaymentStatus
from crud import crud_web_user, crud_web_payment, crud_practise
from db.session import SessionLocalAsync
from models.web_payment import WebPayment
from models.web_user import WebUser
from schemas.web_payment import WebPaymentCreate
from utils.logger import get_logger

logger = get_logger()

Configuration.account_id = settings.UKASSA_SHOPID
Configuration.secret_key = settings.UKASSA_SECRET_KEY


class UkassaPayment:
    def __init__(self, email: str, practise_id: int):
        self.email = email
        self.practise_id = practise_id

    async def _get_web_user(self) -> WebUser:
        async with SessionLocalAsync() as db:
            web_user = await crud_web_user.get_by_email_or_create(db, self.email)

        return web_user

    async def _create_web_payment_in_db(self, web_user_id: int, amount: int) -> WebPayment:
        async with SessionLocalAsync() as db:
            web_payment_schema = WebPaymentCreate(
                payment_id=str(uuid.uuid4()),
                web_user_id=web_user_id,
                practise_id=self.practise_id,
                amount=amount
            )
            return await crud_web_payment.create(db, obj_in=web_payment_schema)

    async def _get_practise(self):
        async with SessionLocalAsync() as db:
            return await crud_practise.get(db, id=self.practise_id)

    async def create_payment(self, amount: int):
        web_user: WebUser = await self._get_web_user()
        if web_user:
            practise = await self._get_practise()
            if practise:
                web_payment_db: WebPayment = await self._create_web_payment_in_db(web_user.id, amount)
                if web_payment_db:
                    idempotence_key = str(web_payment_db.payment_id)
                    payment = Payment.create({
                        "amount": {
                            "value": str(web_payment_db.amount) + ".00",
                            "currency": "RUB"
                        },
                        # "payment_method_data": {
                        #     "type": "bank_card"
                        # },
                        "confirmation": {
                            "type": "redirect",
                            "return_url": settings.RETURN_URL
                        },
                        "description": f"Оплата за курс: {practise.title}",
                        "capture": True,
                    }, idempotence_key)

                    return payment
                else:
                    logger.warning("WebPaymentDb is None")
            else:
                logger.warning("Practise not found")
        else:
            logger.warning("WebUser is None")

        return None

    @staticmethod
    async def find_one(payment_id):
        async with SessionLocalAsync() as db:
            payment_db = await crud_web_payment.get(db, id=payment_id)
            if payment_db:
                payment = Payment.find_one(payment_id)
                if payment.status in UkassaPaymentStatus.keys():
                    payment_db.status = UkassaPaymentStatus[payment.status]
                    db.add(payment_db)
                    await db.commit()
                    await db.refresh(payment_db)
                    return payment_db
                else:
                    logger.error(f"Payment status not recognized: {payment.status}")
                    return None
            else:
                logger.error(f"Payment not found: {payment_id}")
