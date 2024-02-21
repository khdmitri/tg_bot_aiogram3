import asyncio

import aiojobs
import orjson
import redis
import structlog
import tenacity
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ContentType
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import PreCheckoutQuery, Message
from aiohttp import web
from redis.asyncio import Redis

import handlers
import utils
import web_handlers
from data import config
from keyboards.set_menu import set_main_menu
from middlewares import StructLoggingMiddleware
from middlewares.db import UserMiddleware
from middlewares.message_logger import MessageLoggerMiddleware
from utils.bot_instance import BotInstanceSingleton
from utils.constants import BOT_INSTANCE


async def create_db_connections(dp: Dispatcher) -> None:
    logger: structlog.typing.FilteringBoundLogger = dp["business_logger"]

    # logger.debug("Connecting to PostgreSQL", db="main")
    # try:
    #     db_pool = await utils.connect_to_services.wait_postgres(
    #         logger=dp["db_logger"],
    #         host=config.PG_HOST,
    #         port=config.PG_PORT,
    #         user=config.PG_USER,
    #         password=config.PG_PASSWORD,
    #         database=config.PG_DATABASE,
    #     )
    #     dp["db_pool"] = db_pool
    # except tenacity.RetryError:
    #     logger.error("Failed to connect to PostgreSQL", db="main")
    #     exit(1)
    # else:
    #     logger.debug("Succesfully connected to PostgreSQL", db="main")

    if config.USE_CACHE:
        logger.debug("Connecting to Redis")
        try:
            redis_pool = await utils.connect_to_services.wait_redis_pool(
                logger=dp["cache_logger"],
                host=config.CACHE_HOST,
                password=config.CACHE_PASSWORD,
                port=config.CACHE_PORT,
                database=0,
            )
            dp["cache_pool"] = redis_pool
        except tenacity.RetryError:
            logger.error("Failed to connect to Redis")
            exit(1)
        else:
            logger.debug("Succesfully connected to Redis")

    dp["temp_bot_cloud_session"] = utils.smart_session.SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=dp["aiogram_session_logger"],
    )
    if config.USE_CUSTOM_API_SERVER:
        dp["temp_bot_local_session"] = utils.smart_session.SmartAiogramAiohttpSession(
            api=TelegramAPIServer(
                base=config.CUSTOM_API_SERVER_BASE,
                file=config.CUSTOM_API_SERVER_FILE,
                is_local=config.CUSTOM_API_SERVER_IS_LOCAL,
            ),
            json_loads=orjson.loads,
            logger=dp["aiogram_session_logger"],
        )


async def close_db_connections(dp: Dispatcher) -> None:
    if "temp_bot_cloud_session" in dp.workflow_data:
        temp_bot_cloud_session: AiohttpSession = dp["temp_bot_cloud_session"]
        await temp_bot_cloud_session.close()
    if "temp_bot_local_session" in dp.workflow_data:
        temp_bot_local_session: AiohttpSession = dp["temp_bot_local_session"]
        await temp_bot_local_session.close()
    # if "db_pool" in dp.workflow_data:
    #     db_pool: asyncpg.Pool = dp["db_pool"]
    #     await db_pool.close()
    if "cache_pool" in dp.workflow_data:
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]  # type: ignore[type-arg]
        await cache_pool.aclose()


def setup_handlers(dp: Dispatcher) -> None:
    # @dp.pre_checkout_query(lambda query: True)
    # async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    #     await pre_checkout_q.answer(ok=True)

    # @dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
    # async def successful_payment(message: Message):
    #     await message.answer(text="Платеж успешен!")

    dp.include_router(handlers.payment.prepare_router())
    dp.include_router(handlers.user.prepare_router())
    dp.include_router(handlers.admin.prepare_router())


def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))
    dp.update.middleware(UserMiddleware())
    # dp.message.outer_middleware(ThrottlingMiddleware(redis=Redis(
    #     host=config.FSM_HOST,
    #     password=config.FSM_PASSWORD,
    #     port=config.FSM_PORT,
    #     db=0,
    # )))
    dp.update.middleware(MessageLoggerMiddleware())


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = utils.logging.setup_logger().bind(type="aiogram")
    dp["db_logger"] = utils.logging.setup_logger().bind(type="db")
    dp["cache_logger"] = utils.logging.setup_logger().bind(type="cache")
    dp["business_logger"] = utils.logging.setup_logger().bind(type="business")


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiohttp_on_startup(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_startup(**workflow_data)


async def aiohttp_on_shutdown(app: web.Application) -> None:
    dp: Dispatcher = app["dp"]
    for i in [app, *app._subapps]:  # dirty
        if "scheduler" in i:
            scheduler: aiojobs.Scheduler = i["scheduler"]
            scheduler._closed = True
            while scheduler.pending_count != 0:
                dp["aiogram_logger"].info(
                    f"Waiting for {scheduler.pending_count} tasks to complete"
                )
                await asyncio.sleep(1)
    workflow_data = {"app": app, "dispatcher": dp}
    if "bot" in app:
        workflow_data["bot"] = app["bot"]
    await dp.emit_shutdown(**workflow_data)


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(
        webhook_url=config.MAIN_WEBHOOK_ADDRESS
    )
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=config.MAIN_WEBHOOK_ADDRESS.format(
            token=config.BOT_TOKEN, bot_id=config.BOT_TOKEN.split(":")[0]
        ),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=config.MAIN_WEBHOOK_SECRET_TOKEN,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")
    await set_main_menu(bot)


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


async def setup_aiohttp_app(bot: Bot, dp: Dispatcher) -> web.Application:
    scheduler = aiojobs.Scheduler()
    app = web.Application()
    subapps: list[tuple[str, web.Application]] = [
        ("/tg/webhooks/", web_handlers.tg_updates_app),
    ]
    for prefix, subapp in subapps:
        subapp["bot"] = bot
        subapp["dp"] = dp
        subapp["scheduler"] = scheduler
        app.add_subapp(prefix, subapp)
    app["bot"] = bot
    app["dp"] = dp
    app["scheduler"] = scheduler
    app.on_startup.append(aiohttp_on_startup)
    app.on_shutdown.append(aiohttp_on_shutdown)
    return app


async def main() -> None:
    # await async_main()
    aiogram_session_logger = utils.logging.setup_logger().bind(type="aiogram_session")

    if config.USE_CUSTOM_API_SERVER:
        session = utils.smart_session.SmartAiogramAiohttpSession(
            api=TelegramAPIServer(
                base=config.CUSTOM_API_SERVER_BASE,
                file=config.CUSTOM_API_SERVER_FILE,
                is_local=config.CUSTOM_API_SERVER_IS_LOCAL,
            ),
            json_loads=orjson.loads,
            logger=aiogram_session_logger,
        )
    else:
        session = utils.smart_session.SmartAiogramAiohttpSession(
            json_loads=orjson.loads,
            logger=aiogram_session_logger,
        )
    bot = Bot(config.BOT_TOKEN, parse_mode="HTML", session=session)
    dp = Dispatcher(
        storage=RedisStorage(
            redis=Redis(
                host=config.FSM_HOST,
                password=config.FSM_PASSWORD,
                port=config.FSM_PORT,
                db=0,
            ),
            key_builder=DefaultKeyBuilder(with_bot_id=True),
        )
    )
    dp["aiogram_session_logger"] = aiogram_session_logger

    # if config.USE_WEBHOOK:
    #     dp.startup.register(aiogram_on_startup_webhook)
    #     dp.shutdown.register(aiogram_on_shutdown_webhook)
    #     web.run_app(
    #         asyncio.run(setup_aiohttp_app(bot, dp)),
    #         handle_signals=True,
    #         host=config.MAIN_WEBHOOK_LISTENING_HOST,
    #         port=config.MAIN_WEBHOOK_LISTENING_PORT,
    #     )
    # else:
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)
    BOT_INSTANCE["instance"] = bot
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
