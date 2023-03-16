from telebot.async_telebot import AsyncTeleBot
from telebot.types import ForceReply
from telebot.asyncio_storage import StateMemoryStorage
import asyncio
import json
from telebot import asyncio_filters
from utils.keyboards import *
from utils.states import *

class TelegramBroadcast:

    def __init__(self, config) -> None:
        self.config = config
        # Telegram Bot
        
        self.bot_token = self.config['bot_token']
        self.telegram_bot = AsyncTeleBot(self.bot_token,state_storage=StateMemoryStorage())
        self.telegram_bot.add_custom_filter(asyncio_filters.StateFilter(self.telegram_bot))
        self.telegram_bot.add_custom_filter(asyncio_filters.IsDigitFilter())     
        self.subscribers = self.config['subscribers']
        self.admin_chat_id = 1355285614
        self.first_run = True
        @self.telegram_bot.message_handler(commands=['start'])
        async def _start(message):
            await self._start(message)

        @self.telegram_bot.message_handler(commands=['menu'])
        async def _menu(message):
            await self._menu(message)


        @self.telegram_bot.message_handler(state=Broadcast.id)
        async def echo_message(message):
            await self._broadcast_message(message)


        @self.telegram_bot.message_handler(state=Subscriber.name)
        async def add_user_state(message):
            await self._add_user_state(message)

        @self.telegram_bot.message_handler(state=Subscriber.address, is_digit=True)
        async def add_address_state(message):
            await self._add_address_state(message)


        @self.telegram_bot.message_handler(state=[Subscriber.address, RemoveSubscriber.id], is_digit=False)
        async def age_incorrect(message):
            await self._age_incorrect(message)


        @self.telegram_bot.message_handler(state=RemoveSubscriber.id, is_digit=True)
        async def rm_incorrect(message):
            await self._remove_sub(message)



        @self.telegram_bot.callback_query_handler(func=lambda call: True)
        async def callback_query(call):
            if call.data == "cb_broadcast":
                markup = ForceReply()
                await self.telegram_bot.send_message(call.message.chat.id,"Please reply with the message to broadcast to all subscribers.", reply_markup=markup)
                await self.telegram_bot.set_state(call.from_user.id, Broadcast.id, call.message.chat.id)

            elif call.data == "cb_subs":
                kb = subscribers_menu_keyboard()
                await self.telegram_bot.edit_message_reply_markup(message_id=call.message.id,chat_id=call.message.chat.id, reply_markup=kb)
                markup = ForceReply()
                await self.telegram_bot.send_message(call.message.chat.id,"Please reply with the message to broadcast to all subscribers.", reply_markup=markup)
                await self.telegram_bot.set_state(call.from_user.id, Broadcast.id, call.message.chat.id)


            elif call.data == "cb_add_sub":
                    markup = ForceReply()
                    await self.telegram_bot.send_message(call.message.chat.id,"Please enter the name of the subscriber: ",reply_markup=markup)
                    await self.telegram_bot.set_state(call.from_user.id, Subscriber.name, call.message.chat.id)
                

            elif call.data == "cb_remove_sub":
                markup = ForceReply()
                await self.telegram_bot.send_message(call.message.chat.id,"Please enter the user id of the subscriber: ",reply_markup=markup)
                await self.telegram_bot.set_state(call.from_user.id, RemoveSubscriber.id, call.message.chat.id)


            elif call.data == "mm_back":
                kb = main_menu_keyboard()    
                await self.telegram_bot.edit_message_reply_markup(message_id=call.message.id,chat_id=call.message.chat.id, reply_markup=kb)

    def save_config(self):
        json.dump(self.config, open('config.json','w'))


    async def _start(self, message):
        if self.first_run:
            self.first_run = False
            self.admin_chat_id = message.chat.id
            await self.telegram_bot.reply_to(message, "Hi, welcome to the broadcast bot! You are now admin for this bot only you can use this bot.\nTo start, hit \menu")
            return

        elif message.chat.id!=self.admin_chat_id:
            await self.telegram_bot.reply_to(message, "You are not authorized to use this command.")
            return
        else:
            await self.telegram_bot.reply_to(message, "Hi, welcome to the broadcast bot! You are now admin for this bot only you can use this bot.\nTo start, hit /\menu")
            return


    async def _menu(self, message):
        if message.chat.id!=self.admin_chat_id:
            await self.telegram_bot.reply_to(message, "You are not authorized to use this command.")
            return
        kb = main_menu_keyboard()
        await self.telegram_bot.reply_to(message, """\
                                                    Hi, you can choose options from below:\
                                                    """,reply_markup=kb)
        




      
    async def _broadcast_message(self, message):
        for subscriber in self.subscribers:
            chat_id = list(subscriber.values())[0]
            self.telegram_bot.forward_message(chat_id, message.chat.id, message.id)
        
        await self.telegram_bot.send_message(message.chat.id, "Message has been broadcasted to all subscribers.")
        await self.telegram_bot.delete_state(message.from_user.id, message.chat.id)



    async def _remove_sub(self, message):
        try:
            subs_id = int(message.text)
            new_list = []
            name = None
            for subscriber in self.subscribers:
                if str(list(subscriber.values())[0])!=str(subs_id):
                    new_list.append(subscriber)
                else:
                    name = list(subscriber.keys())[0]

            self.subscribers = new_list
            await self.telegram_bot.reply_to(message, f"User: {name} is removed from subscribers!")
            await self.telegram_bot.delete_state(message.from_user.id,  message.chat.id)
        except:
            await self.telegram_bot.reply_to(message, f"Please provide valid subscriber id.\n/remove_user 12345564")
        self.config['subscribers'] = self.subscribers
        self.save_config()




    async def _age_incorrect(self, message):
        await self.telegram_bot.send_message(message.chat.id,"This can only be a number.")

    async def _add_address_state(self, message):
        
        async with self.telegram_bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['address'] = message.text  
            new_subs = {data['name'] : int(data['address'])}
            if int(int(data['address'])) not in list([list(x.values())[0] for x in self.subscribers]):
                self.subscribers.append(new_subs)
                self.binance.subscribers = self.subscribers
                self.bybit.subscribers = self.subscribers
                self.bitget.subscribers = self.subscribers
                self.kucoin.subscribers = self.subscribers
                await self.telegram_bot.reply_to(message, f'Group {data["name"]} with id {data["address"]} is sucessfully registered.')
        await self.telegram_bot.delete_state(message.from_user.id,  message.chat.id)
        self.config['subscribers'] = self.subscribers
        self.save_config()
    
    async def _add_user_state(self, message):
        markup = ForceReply()
        await self.telegram_bot.send_message(message.chat.id, f'Please enter the chat id for this group: ',reply_markup=markup)
        await self.telegram_bot.set_state(message.from_user.id, Subscriber.address, message.chat.id)
        async with self.telegram_bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['name'] = message.text


    def run(self):        
        asyncio.run(self.telegram_bot.infinity_polling())



if __name__=="__main__":
    config = json.load(open('config.json'))
    bot = TelegramBroadcast(config=config)
    
    while True:
        bot.run()
        print('Looping Again')