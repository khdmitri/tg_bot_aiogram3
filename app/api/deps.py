from typing import Generator

from db.session import SessionLocalAsync


async def get_db_async() -> Generator:
    async with SessionLocalAsync() as session:
        yield session
