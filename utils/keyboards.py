from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def subscribers_menu_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
                    InlineKeyboardButton("List Groups", callback_data="cb_list_subs"),
                    InlineKeyboardButton("Add Subscriber", callback_data="cb_add_sub"),
                    InlineKeyboardButton("Remove Subscriber", callback_data="cb_remove_sub"),
                    )
                    
    markup.add(InlineKeyboardButton("🔙Back", callback_data="mm_back"))
    return markup

def main_menu_keyboard():

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("✉️ Broadcast", callback_data="cb_broadcast"),
        InlineKeyboardButton("✉️ Manange Subscribers", callback_data="cb_subs"),
    )

    return markup