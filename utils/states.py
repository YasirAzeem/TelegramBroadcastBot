from telebot.asyncio_handler_backends import State, StatesGroup

class Subscriber(StatesGroup):
    name = State()
    address = State()


class RemoveSubscriber(StatesGroup):
    id = State()


class Broadcast(StatesGroup):
    id = State()