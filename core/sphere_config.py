from typing import List, Union

from crud import crud_sphere, crud_depth
from db.session import SessionLocalAsync
from schemas import SphereWebUser


def get_level(value: int):
    if value <= 25:
        return 1
    elif value <=50:
        return 2
    elif value <=75:
        return 3
    else:
        return 4


class SphereConfig:
    def __init__(self, web_user_id: Union[int | None], sphere_list: List[SphereWebUser]):
        sphere_list.sort(key=lambda x: x.depth)
        self.sphere_list = sphere_list
        self.web_user_id = web_user_id

    async def prepare_practise(self):
        practise = []
        async with SessionLocalAsync() as db:
            for sphere in self.sphere_list:
                sphere_db = await crud_sphere.get(db, id=sphere.id)
                if sphere_db:
                    for lvl in range(0, sphere.depth):
                        depth_db = await crud_depth.get(db, id=lvl+1)
                        practise.append({
                            "meditation": sphere_db.as_dict(),
                            "practise": depth_db.as_dict()
                        })

        return practise
