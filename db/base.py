# Import all the models, so that Base has them before being
# imported by Alembic
from models.user import User, UserPayment, Invoice
from models.media import Media
from models.practise import Practise
from .base_class import Base

