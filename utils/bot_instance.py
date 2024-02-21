from aiogram import Bot


class BotInstanceSingleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BotInstanceSingleton, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._bot_instance = None

    def init_bot_instance(self, bot: Bot):
        self._bot_instance = bot

    def get_instance(self) -> Bot:
        return self._bot_instance
