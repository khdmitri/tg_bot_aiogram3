from crud.base import CRUDBase
from models.sphere import Sphere, Depth
from schemas import SphereCreate, SphereUpdate
from schemas.depth import DepthCreate, DepthUpdate


class CRUDDepth(CRUDBase[Depth, DepthCreate, DepthUpdate]):
    pass


crud_depth = CRUDDepth(Depth)
