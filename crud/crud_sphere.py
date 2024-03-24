from crud.base import CRUDBase
from models.sphere import Sphere
from schemas import SphereCreate, SphereUpdate


class CRUDSphere(CRUDBase[Sphere, SphereCreate, SphereUpdate]):
    pass


crud_sphere = CRUDSphere(Sphere)
