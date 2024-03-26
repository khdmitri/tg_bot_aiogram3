from typing import List

from app.core.config import settings
from crud import crud_practise
from db.session import SessionLocalAsync


async def get_practise_price(practise_id: int, discount=settings.PRACTISE_DISCOUNT):
    async with SessionLocalAsync() as db:
        practise = await crud_practise.get(db, id=practise_id)
        if practise:
            total = practise.cost
            full_total = total * (100 + discount) / 100
            # for media in practise.medias:
            #     if media.cost > 0:
            #         full_total += media.cost

            # total = full_total * (100 - discount) / 100

            return int(full_total), int(total)

    return 0, 0

