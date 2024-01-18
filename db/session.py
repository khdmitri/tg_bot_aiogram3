from typing import Generator

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from data import config
from db.base_class import Base

SQLALCHEMY_DATABASE_URI_ASYNC = PostgresDsn.build(
    scheme="postgresql+asyncpg",
    username=config.PG_USER,
    password=config.PG_PASSWORD,
    host=config.PG_HOST,
    port=int(config.PG_PORT),
    path=f"{config.PG_DATABASE or ''}",
)

engine = create_async_engine(str(SQLALCHEMY_DATABASE_URI_ASYNC),
                             echo=False, pool_size=20, max_overflow=0,
                             pool_recycle=1500,
                             connect_args={
                                 "server_settings": {"tcp_keepalives_idle": "600"}
                             })
SessionLocalAsync = async_sessionmaker(engine, expire_on_commit=False)


async def get_db_async() -> Generator:
    async with SessionLocalAsync() as session:
        yield session


async def get_new_session() -> AsyncSession:
    db_gen = get_db_async()
    return await anext(db_gen)

# async def async_main():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
