import asyncio
import datetime
import logging

from aiogram import Bot
from aiogram.utils.markdown import hlink
from pyqiwi import Wallet
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from db.db import SessionLocal
from models.user.models import Invoice, UserPayment, User

logger = logging.getLogger(__name__)


class NotEnoughMoney(Exception):
    pass


async def send2admins(bot: Bot, text: str, db_session: Session):
    admins = db_session.query(User).filter(User.is_admin)
    for admin in admins:
        await bot.send_message(admin.tg_id, text, parse_mode="HTML")


def update_user_amount(user, amount, db_session):
    setattr(user, "internal_amount", amount)
    db_session.commit()
    db_session.refresh(user)
    return user


mention_template = "tg://user?id={user_id}"


async def create_payment(invoice: Invoice, db_session: Session, bot: Bot):
    payment = UserPayment(
        paid_amount=invoice.amount,
        user_id=invoice.user_id,
        media_id=invoice.media_id,
        practise_id=invoice.practise_id,
        invoice_id=invoice.id
    )
    setattr(invoice, "status", "PAID")
    db_session.add(payment)
    db_session.commit()
    db_session.refresh(payment)
    db_session.refresh(invoice)

    if invoice.media_id is None and invoice.practise_id is None:
        # Private lesson
        link = hlink("Пользователь", mention_template.format(user_id=invoice.user.tg_id))
        await send2admins(bot, "\n".join([
            link+f" оплатил частный урок с ID={invoice.id}",
            "Свяжитесь к клиентом как можно скорее, согласуйте время и тему занятия.",
            "По окончанию урока, сделайте отметку о выполнении, используя команду /private_done (ID)"
        ]), db_session)

    return payment


async def check_payments(wallet: Wallet, bot: Bot, interval=60):
    db_session = SessionLocal()
    while True:
        await asyncio.sleep(interval)
        try:
            transactions = wallet.history(
                start_date=datetime.datetime.now()-datetime.timedelta(seconds=interval+5)).get("transactions")
            # transactions = wallet.history(
            #     start_date=datetime.datetime.now() - datetime.timedelta(days=1)).get("transactions") #Test case
            if not db_session.is_active:
                db_session = SessionLocal()

            for transaction in transactions:
                paid_amount = float(transaction.total.amount)
                try:
                    invoice = db_session.query(Invoice).filter(Invoice.uuid == transaction.comment,
                                                               Invoice.status == "CREATED").one()
                    if paid_amount >= float(invoice.amount):
                        # if paid_amount >= 2: #Test only
                        await create_payment(invoice, db_session, bot)
                        await bot.send_message(invoice.user.tg_id,
                                               f"Счет №{invoice.uuid} успешно оплачен!")
                        change = int(paid_amount - invoice.amount)
                        if change > 0:
                            amount = invoice.user.internal_amount+change
                            update_user_amount(invoice.user, amount, db_session)
                            await bot.send_message(invoice.user.tg_id, "\n".join(
                                [
                                    f"Излишне оплаченная сумма добавлена на Ваш внутренний баланс.",
                                    f"Теперь на Вашем балансе: <b>{invoice.user.internal_amount}</b>"
                                ]
                            ))
                    else:
                        # Not Enough Money
                        diff = invoice.amount - transaction.total.amount
                        # diff = 1 - transaction.total.amount #Test case
                        if invoice.user.internal_amount >= diff:
                            update_user_amount(invoice.user, int(invoice.user.internal_amount-diff), db_session)
                            await create_payment(invoice, db_session, bot)
                            await bot.send_message(invoice.user.tg_id,
                                                   f"Счет №{invoice.uuid} успешно оплачен!")
                            await bot.send_message(invoice.user.tg_id, "\n".join(
                                [
                                    f"Недостающая сумма добавлена с Вашего внутреннего баланса.",
                                    f"Теперь на Вашем балансе: <b>{invoice.user.internal_amount}</b>"
                                ]
                            ))
                        else:
                            update_user_amount(invoice.user,
                                               int(invoice.user.internal_amount+transaction.total.amount),
                                               db_session)
                            await bot.send_message(invoice.user.tg_id, "\n".join(
                                [
                                    f"Оплаченная сумма не достаточна. Оплата перечислена на Ваш внутренний баланс.",
                                    f"Теперь на Вашем балансе: <b>{invoice.user.internal_amount}</b>"
                                ]
                            ))
                except NoResultFound:
                    pass
        except Exception as e:
            logger.error(f"CheckPayments: {str(e)}")
