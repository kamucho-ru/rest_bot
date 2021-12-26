import telebot
from telebot import types

token = 'secret:token'

lang = None
curr_menu = None
cart = {}

messages = []

langs = [
    ('Русский', 'set_rus_lang'),
    ('English', 'set_eng_lang'),
    # ('Hindi', 'set_hin_lang'),
]

translations = {
    'rus': {
        'Cart: {} pcs = {} rs.': 'Корзина: {} шт = {} руп.',
        '{}, {} pcs * {} rs. = {} rs.': '{}, {} шт * {} руп. = {} руп.',
        '<< back <<': '<< Назад <<',
        'Please select ': 'Сделайте ваш выбор ',
        'Select positions for delete or proceed to order':
            'Выберите позиции для удаления или перейдите к оформлению заказа',
        'Proceed to order': 'Перейти к оформлению заказа',
        'Under construction. Please back later...': 'В разработке. Попробуйте повторить позже...',
    },
    'hin': {

    },
}

drinks = {
    'Tea': {
        'Black': ['Plain black tea', 'picture_url', 50],
        'Milk': ['Tea with milk', 'picture_url', 50],
        'Masala': ['Masala tea', 'picture_url', 50],
    },
    'Coffee': {
        'Black': ['Plain black coffee', 'picture_url', 50],
        'Milk': ['Coffee with milk', 'picture_url', 50],
        'Masala': ['Masala coffee', 'picture_url', 50],
    },
    'Combucha': ['Descr/ingridients', 'picture_url', 50],
}

menu = {
    'Full menu': {
        'Hot dishes': {
            'Pulao': ['Rice, pork, veges & spices', 'picture_url', 230],
            'Soup': ['Pea sou, veggies', 'picture_url', 50],
            'French fries': ['Fried potatoes', 'picture_url', 50],
        },
        'Salads': {
            'Olivie': {
                'Olivie (chicken)': ['Olivie with chicken', 'picture_url', 140],
                'Olivie (tofu)': ['Olivie with tofu', 'picture_url', 140],
            },
            'Achik chuchuk': ['Marinated onion with tomatoes', 'picture_url', 100],
            'Spring': ['Cabbage, carrot, onion', 'picture_url', 100],
            'Beetroot&garlic': ['Beetroot, garlic, mayonese', 'picture_url', 100],
        },
        'Drinks': drinks,
    },
    'Veg menu': {
        'Hot dishes': {
            'Soup': ['Pea sou, veggies', 'picture_url', 50],
            'French fries': ['Fried potatoes', 'picture_url', 50],
        },
        'Salads': {
            'Olivie (tofu)': ['Olivie with tofu', 'picture_url', 140],
            'Achik chuchuk': ['Marinated onion with tomatoes', 'picture_url', 100],
            'Spring': ['Cabbage, carrot, onion', 'picture_url', 100],
            'Beetroot&garlic': ['Beetroot, garlic, mayonese', 'picture_url', 100],
        },
        'Drinks': drinks,
    },
    'Drinks': drinks
}

bot = telebot.TeleBot(token)


def reset_settings():
    global lang, curr_menu, cart
    lang = None
    curr_menu = None
    cart = {}


def get_translation(s):
    global lang, translations
    if lang == 'eng':
        return s
    return translations.get(lang, {}).get(s, s)


def get_concrete_data(crnt, default=menu):
    if crnt is None:
        return default

    if ':' in crnt:
        return get_concrete_data(
            ':'.join(crnt.split(':')[1:]),
            default[crnt.split(':')[0]]
        )
    return default[crnt]


def show_menu(message, show_cart=False):
    global lang, curr_menu, menu, cart, messages

    def make_menu_keyboard(current):
        keyboard = types.InlineKeyboardMarkup()

        def add_buttons(submenu_data, prev_path):
            for i in submenu_data:
                if isinstance(submenu_data[i], list):
                    text_ = f'{i} [{submenu_data[i][0]}]  / {submenu_data[i][2]}'
                    callback_ = f'order_{prev_path}{i}'
                else:
                    text_ = i
                    callback_ = f'open_menu_{prev_path}{i}'

                item_key = types.InlineKeyboardButton(text=text_, callback_data=callback_)
                keyboard.add(item_key)

        data_ = get_concrete_data(current)
        add_buttons(data_, '' if not current else f'{current}:')
        return keyboard

    if not show_cart:
        keyboard = make_menu_keyboard(curr_menu)
        if cart:
            cart_items = 0
            cart_price = 0
            for c in cart:
                cart_items += int(cart[c][3])
                cart_price += int(cart[c][3]) * int(cart[c][2])
            item_key = types.InlineKeyboardButton(
                text=get_translation('Cart: {} pcs = {} rs.').format(cart_items, cart_price),
                callback_data='order_proceed'
            )
            keyboard.add(item_key)
    else:
        keyboard = types.InlineKeyboardMarkup()
        if cart:
            for c in cart:
                item_key = types.InlineKeyboardButton(
                    text=get_translation('{}, {} pcs * {} rs. = {} rs.').format(
                        cart[c][0], cart[c][3], cart[c][2], cart[c][2]*cart[c][3]),
                    callback_data='remove_from_cart')
                keyboard.add(item_key)
        item_key = types.InlineKeyboardButton(
            text=get_translation('Proceed to order'),
            callback_data='order_proceed_2')
        keyboard.add(item_key)

    # Назад или сразу полное меню
    if curr_menu:
        item_key = types.InlineKeyboardButton(
            text=get_translation('<< back <<'),
            callback_data='go_back'
        )
        keyboard.add(item_key)

    # очистка сообщений
    for m in messages:
        bot.delete_message(m.chat.id, message.id)
        messages.remove(m)

    messages.append(message)

    question = get_translation('Please select ')
    if curr_menu:
        question += curr_menu
    if show_cart:
        question = get_translation('Select positions for delete or proceed to order')
    bot.send_message(message.chat.id, text=question, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])  # ['text', 'document', 'audio']
def get_text_messages(message):
    global lang

    if message.text == '/clear':
        reset_settings()

    if not lang:
        keyboard = types.InlineKeyboardMarkup()

        for lang, call in langs:
            lang_key = types.InlineKeyboardButton(text=lang, callback_data=call)
            keyboard.add(lang_key)
        question = '?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
        show_menu(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global lang, curr_menu, cart
    show_cart = False
    if call.data.startswith('set_') and call.data.endswith('_lang'):
        lang = call.data[4:-5]
        # bot.register_next_step_handler(message, get_age)
    elif call.data.startswith('open_menu_'):
        curr_menu = call.data[10:]
    elif call.data == 'order_proceed':
        show_cart = True
    elif call.data == 'order_proceed_2':
        bot.send_message(
            call.message.chat.id,
            text=get_translation('Under construction. Please back later...')
        )
    elif call.data == 'go_back':
        if ':' not in curr_menu:
            curr_menu = None
        else:
            curr_menu = ':'.join(curr_menu.split(':')[:-1])
    elif call.data.startswith('order_'):
        ordered_item = get_concrete_data(call.data[6:])
        name = call.data.split(':')[-1]
        content = ordered_item
        if name not in cart:
            content.append(1)  # amount
            cart[name] = content
        else:
            cart[name][3] += 1

    show_menu(call.message, show_cart)


bot.polling(none_stop=True, interval=0)
