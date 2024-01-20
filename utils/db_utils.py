from sqlalchemy.ext.asyncio import AsyncSession

from crud import crud_media
from crud.crud_media import CRUDMedia
from crud.crud_practise import CRUDPractise


async def swap_orders(db: AsyncSession, ids: list, crud: CRUDMedia | CRUDPractise):
    swap_a = await crud.get(db, id=ids[0])
    swap_b = await crud.get(db, id=ids[1])

    order_a = swap_a.order
    order_b = swap_b.order

    swap_a.order = order_b
    swap_b.order = order_a

    db.add(swap_a)
    db.add(swap_b)
    await db.commit()
    await db.refresh(swap_a)
    await db.refresh(swap_b)
