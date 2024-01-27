from enum import Enum


class MessageTypes(Enum):
    PHOTO = 1
    VIDEO = 2
    MEDIA_GROUP = 3
    TEXT_MESSAGE = 4
    NOT_DEFINED = 0


class PractiseCategories(Enum):
    LESSON = 1
    ONLINE = 2

# if __name__ == '__main__':
#     var = MessageTypes.PHOTO
#     print(var)
#     print(MessageTypes.VIDEO.value)
