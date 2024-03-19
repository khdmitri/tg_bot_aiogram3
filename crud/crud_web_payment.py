from crud.base import CRUDBase
from models.web_payment import WebPayment
from schemas.web_payment import WebPaymentCreate, WebPaymentUpdate


class CRUDWebPayment(CRUDBase[WebPayment, WebPaymentCreate, WebPaymentUpdate]):
    pass


crud_web_payment = CRUDWebPayment(WebPayment)
