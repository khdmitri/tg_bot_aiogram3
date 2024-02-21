from aiogram import Bot


class BotInstanceSingleton(object):
    _bot_instance = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(BotInstanceSingleton, cls).__new__(cls)
        return cls.instance

    def init_bot_instance(self, bot: Bot):
        print("Current Bot Instance:", self._bot_instance)
        self._bot_instance = bot
        print("=== Current Bot Instance:", self._bot_instance)

    def get_instance(self) -> Bot:
        print("GET: Current Bot Instance:", self._bot_instance)
        return self._bot_instance
