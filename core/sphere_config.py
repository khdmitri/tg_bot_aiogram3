import traceback
from typing import List, Union

from crud import crud_sphere, crud_depth, crud_sphere_user
from db.session import SessionLocalAsync
from schemas import SphereWebUser, SphereUserCreate
from utils.logger import get_logger

logger = get_logger()


def get_level(value: int):
    if value <= 25:
        return 4
    elif value <=50:
        return 3
    elif value <=75:
        return 2
    else:
        return 1


class SphereConfig:
    def __init__(self, web_user_id: Union[int | None], sphere_list: List[SphereWebUser]):
        # sphere_list.sort(key=lambda x: x.depth)
        self.sphere_list = sphere_list
        self.web_user_id = web_user_id

    async def prepare_practise(self):
        practise = []
        self.sphere_list.sort(key=lambda x: x.depth)
        async with SessionLocalAsync() as db:
            for sphere in self.sphere_list:
                sphere_db = await crud_sphere.get(db, id=sphere.id)
                if sphere_db:
                    for lvl in range(0, get_level(sphere.depth)):
                        depth_db = await crud_depth.get(db, id=lvl+1)
                        if depth_db:
                            practise.append({
                                "meditation": sphere_db.as_dict(),
                                "practise": depth_db.as_dict()
                            })
        return practise

    async def update_practise(self):
        async with SessionLocalAsync() as db:
            spheres = await crud_sphere.get_multi(db)
            old_practise = await crud_sphere_user.get_by_user_id(db, self.web_user_id)
            await crud_sphere_user.clean_by_user_id(db, user_id=self.web_user_id)
            for sphere in self.sphere_list:
                new_sphere_user = SphereUserCreate(
                    web_user_id=self.web_user_id,
                    order=sphere.depth,
                    depth=get_level(sphere.depth),
                    sphere_id=sphere.id
                )
                await crud_sphere_user.create(db, obj_in=new_sphere_user)
            new_practise = await crud_sphere_user.get_by_user_id(db, self.web_user_id)
            if old_practise:
                compare_results = []
                for ind, old_item in enumerate(old_practise):
                    try:
                        diff = int(new_practise[ind].depth - old_item.depth)
                        compare_results.append(
                            [spheres[old_item.sphere_id-1].title, old_item.depth, new_practise[ind].depth, diff]
                        )
                    except Exception:
                        logger.error(traceback.format_exc())
                return compare_results
            else:
                return None
