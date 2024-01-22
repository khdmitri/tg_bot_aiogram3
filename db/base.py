# Import all the models, so that Base has them before being
# imported by Alembic
from db.base_class import Base # noqa
from models.user import User, UserPayment, Invoice # noqa
from models.media import Media # noqa
from models.practise import Practise # noqa
from models.post import Post # noqa
from models.media_group import MediaGroup # noqa
