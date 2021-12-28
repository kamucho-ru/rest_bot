import telebot
from telebot import types

from data import langs, menu, translations  # noqa
from settings import DEBUG, managers, token  # noqa

# searate carts for users
cart = {
    # 'user_id': {
    #     'cart': {},
    #     'order_type': {},
    #     'pay_type': {},
    #     'comments': {},
    # }
}

lang = {
    # 'user_id': 'smth'
}
curr_menu = {
    # 'user_id': 'smth'
}

# order_type
REST = 'REST'
AWAY = 'AWAY'
DLVR = 'DLVR'

# pay_type
CASH = 'CASH'
PHPE = 'PHNE'

messages = {
    # 'user_id': []
}

known_users = []
f = open('known_users.txt', 'r')
x = f.readline()  # headers
while x:
    x = f.readline()
    if '::' in x:
        known_users.append(x.split('::')[0])
f.close()

bot = telebot.TeleBot(token)


def logger(message):
    global DEBUG
    if DEBUG:
        print(message)
    # else log somewhere else


def reset_settings(user_id, soft=False):
    global lang, curr_menu, cart
    if not soft:
        lang[user_id] = None
    curr_menu[user_id] = None
    del cart[user_id]


def get_translation(s, user_id):
    global lang, translations
    current_language = lang.get(user_id, 'eng')
    if current_language == 'eng':
        return s
    return translations.get(current_language, {}).get(s, s)


def get_concrete_data(crnt, default=menu):
    if crnt is None:
        return default

    if ':' in crnt:
        return get_concrete_data(':'.join(crnt.split(':')[1:]), default[crnt.split(':')[0]])
    return default[crnt]


def track_and_clear_messages(message, and_clear=True):
    global messages

    if message.chat.id not in messages:
        messages[message.chat.id] = []
    not_inserted = True

    for m in messages[message.chat.id]:
        if m.id == message.id:
            not_inserted = False

        if and_clear:
            try:
                bot.delete_message(m.chat.id, m.id)
            except Exception as e:
                logger(
                    'EXCEPTION WARNING while deleting message "{}" ({}): {}'.format(
                        m.text, m.id, e
                    )
                )
            messages[message.chat.id].remove(m)
    logger(
        'track message "{}" ({}), already there (={}): [{}]'.format(
            message.text,
            message.id,
            'no' if not_inserted else 'yes',
            [(m.text, m.id) for m in messages[message.chat.id]],
        )
    )
    if not_inserted:
        messages[message.chat.id].append(message)


def get_current_cart(user_id):
    global cart, REST

    if user_id not in cart:
        cart[user_id] = {
            'cart': {},
            'order_type': REST,
            'pay_type': None,
        }

    return cart[user_id]


def check_lang(user_id):
    global lang, langs
    m_ = False
    current_language = lang.get(user_id)
    logger(f'current_language is {current_language}')
    if not current_language:
        keyboard = types.InlineKeyboardMarkup()

        for lang_name, call in langs:
            lang_key = types.InlineKeyboardButton(text=lang_name, callback_data=call)
            keyboard.add(lang_key)
        question = '?'
        m_ = bot.send_message(user_id, text=question, reply_markup=keyboard)
        track_and_clear_messages(m_, False)
    logger(
        'Language check for {}: {} ({})'.format(user_id, True if m_ else False, lang.get(user_id))
    )
    return m_


def cut_description(descr, text_len):
    # receive minus amount of symbols, that are already presented in text
    max_descr_len = text_len + 62  # add maximum length constant
    return descr if len(descr) <= max_descr_len else descr[: max_descr_len - 3] + ' ..'


def show_menu(message, show='menu'):
    logger('showing menu, type' + show)
    global lang, curr_menu, menu, cart
    messages_stack = []
    current_cart = get_current_cart(message.chat.id)

    def make_keyboard(current):
        keyboard = types.InlineKeyboardMarkup()

        def add_menu_buttons(submenu_data, prev_path):
            for i in submenu_data:
                if isinstance(submenu_data[i], list):
                    template_text = '{} [{}] / {}'
                    name = i

                    description = cut_description(
                        submenu_data[i][0],
                        6 - len(template_text) - len(name) - len(str(submenu_data[i][2])),
                    )

                    text_ = template_text.format(name, description, submenu_data[i][2])
                    callback_ = 'open_item_' + prev_path + i  # for showing product info
                    callback_ = 'order_' + prev_path + i
                else:
                    text_ = i
                    callback_ = 'open_menu_' + prev_path + i

                item_key = types.InlineKeyboardButton(text=text_, callback_data=callback_)
                keyboard.add(item_key)

        if current:
            keyboard.add(
                types.InlineKeyboardButton(
                    text=get_translation('Go to top menu', message.chat.id),
                    callback_data='open_menu',
                )
            )
        data_ = get_concrete_data(current)
        logger(type(data_))
        if isinstance(data_, dict):
            add_menu_buttons(data_, '' if not current else (current + ':'))
        else:
            logger('WARNING!! for path {current} not possible make menu')

        return keyboard

    if show == 'cart':
        # show cart content
        keyboard = types.InlineKeyboardMarkup()
        for c in current_cart['cart']:
            template_text = get_translation('{} [{}] * {} = {} rs.', message.chat.id)
            name = c
            amount = str(current_cart['cart'][c][3])
            total = str(current_cart['cart'][c][2] * current_cart['cart'][c][3])

            # max length of button string is 280, plus 2 symbols ({} for each variable) in template
            description = cut_description(
                current_cart['cart'][c][0],
                8 - len(template_text) - len(name) - len(amount) - len(total),
            )

            item_key = types.InlineKeyboardButton(
                text=template_text.format(name, description, amount, total),
                callback_data='remove_order_{}'.format(current_cart['cart'][c][4]),
            )
            keyboard.add(item_key)
        item_key = types.InlineKeyboardButton(
            text=get_translation('Proceed to order', message.chat.id),
            callback_data='order_proceed_2',
        )
        keyboard.add(item_key)

    elif show == 'product':
        # show info about product and order buttons
        data = get_concrete_data(curr_menu.get(message.chat.id))
        text = '***___{}___***</b>\n{}, {} rs.'.format(
            curr_menu.get(message.chat.id).split(':')[-2], data[0], data[2]
        )
        messages_stack.append(text)
        # send picture with url data_[1]
        # m_ = bot.send_message(message.chat.id, text=question)
        # track_and_clear_messages(m_, False)
        # track_and_clear_messages(product_description, 'track_only')
        # track_and_clear_messages(product_description, 'track_only')
        # todo need to keep item's messages while changing count of items

        keyboard = types.InlineKeyboardMarkup()
        item_key = types.InlineKeyboardButton(
            text=get_translation('Add 1', message.chat.id),
            callback_data='order_' + curr_menu.get(message.chat.id),
        )
        keyboard.add(item_key)

        for i in current_cart['cart']:
            if current_cart['cart'][i][0] == data[0] and current_cart['cart'][i][2] == data[2]:
                if current_cart['cart'][i][3] > 0:
                    item_key = types.InlineKeyboardButton(
                        text=get_translation('Remove 1', message.chat.id),
                        callback_data='remove_order_' + curr_menu.get(message.chat.id),
                    )
                    keyboard.add(item_key)

    else:  # if show == 'menu':
        # show current menu
        keyboard = make_keyboard(curr_menu.get(message.chat.id))

    if current_cart['cart'] and show != 'cart':
        cart_items = 0
        cart_price = 0
        for c in current_cart['cart']:
            cart_items += int(current_cart['cart'][c][3])
            cart_price += int(current_cart['cart'][c][3]) * int(current_cart['cart'][c][2])
        item_key = types.InlineKeyboardButton(
            text=get_translation('Cart: {} items = {} rs.', message.chat.id).format(
                cart_items, cart_price
            ),
            callback_data='order_proceed',
        )
        keyboard.add(item_key)

    question = get_translation('Please select ', message.chat.id)

    # Назад или сразу полное меню
    if curr_menu.get(message.chat.id):
        item_key = types.InlineKeyboardButton(
            text=get_translation('<< back', message.chat.id), callback_data='go_back'
        )
        keyboard.add(item_key)
        question = curr_menu.get(message.chat.id).lower().replace(':', ' > ')

    if show == 'cart':
        question = get_translation(
            'Select positions for delete or proceed to order', message.chat.id
        )

    track_and_clear_messages(message)

    for m in messages_stack:
        m_ = bot.send_message(message.chat.id, text=question)
        track_and_clear_messages(m_, False)
        question = m

    m_ = bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
    track_and_clear_messages(m_)


@bot.message_handler(content_types=['text'])  # ['text', 'document', 'audio']
def get_text_messages(message):
    logger('message received')
    global DEBUG

    track_and_clear_messages(message)

    if str(message.chat.id) not in known_users:
        f = open('known_users.txt', 'a')
        f.write(
            '{}::{}::{}::Auto added\n'.format(
                message.chat.id, message.chat.username, lang.get(message.chat.id, None)
            )
        )
        if not message.chat.username:
            bot.forward_message(managers[0], message.chat.id, message.id)
            bot.send_message(managers[0], text=f'Forwarded from {message.chat.id} {message.chat}')
        known_users.append(message.chat.id)
        f.close()

    if message.text == '/clear':
        reset_settings(message.chat.id)

    if not check_lang(message.chat.id):
        show_menu(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        logger(
            'callback_worker from {} : {} [{}]'.format(
                call.message.chat.username, call.data, call.message.text
            )
        )
        global lang, curr_menu, cart
        show_type = 'menu'

        current_cart = get_current_cart(call.message.chat.id)

        check_lang(call.message.chat.id)

        if call.data.startswith('set_') and call.data.endswith('_lang'):
            # set language
            lang[call.message.chat.id] = call.data[4:-5]

        elif call.data == 'open_menu':
            # Show top
            curr_menu[call.message.chat.id] = None

        elif call.data.startswith('open_menu_'):
            # show submenu
            curr_menu[call.message.chat.id] = call.data[10:]

        elif call.data.startswith('open_item_'):
            # show product info
            show_type = 'product'
            curr_menu[call.message.chat.id] = call.data[10:]

        elif call.data == 'order_proceed':
            show_type = 'cart'
            # todo flush product_info

        elif call.data == 'order_proceed_2':
            keyboard = types.InlineKeyboardMarkup()

            item_key = types.InlineKeyboardButton(
                text=get_translation('Order at restaurant', call.message.chat.id),
                callback_data='order_proceed_restaurant',
            )
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(
                text=get_translation('Takeaway from restaurant', call.message.chat.id),
                callback_data='order_proceed_takeaway',
            )
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(
                text=get_translation('Delivery', call.message.chat.id),
                callback_data='order_proceed_delivery',
            )
            keyboard.add(item_key)

            text = get_translation('Choose order type', call.message.chat.id)

            m_ = bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)
            track_and_clear_messages(m_)
            return
        elif call.data in [
            'order_proceed_delivery',
            'order_proceed_takeaway',
            'order_proceed_restaurant',
        ]:
            if call.data == 'order_proceed_delivery':
                current_cart['order_type'] = DLVR
                # если доставка - спросить локацию
            elif call.data == 'order_proceed_takeaway':
                current_cart['order_type'] = AWAY

            # show payment options
            # способ оплаты - кэш/phonepe
            keyboard = types.InlineKeyboardMarkup()

            item_key = types.InlineKeyboardButton(
                text=get_translation('Cash', call.message.chat.id),
                callback_data='order_proceed_cash',
            )
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(
                text=get_translation('PhonePe', call.message.chat.id),
                callback_data='order_proceed_phonepe',
            )
            keyboard.add(item_key)

            text = get_translation('Choose payment type', call.message.chat.id)

            m_ = bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)
            track_and_clear_messages(call.message, False)
            track_and_clear_messages(m_)
            return

        elif call.data == 'order_proceed_4':
            # discount info
            # скидка 10%? - промокод или ссылка на отзыв (скриншот)
            pass

        elif call.data in ['order_proceed_cash', 'order_proceed_phonepe']:
            # сообщение менеджерам о новом заказе
            cart_text = '\n'.join(
                [
                    '{} [{}] x {} = {}'.format(
                        c,
                        current_cart['cart'][c][0],
                        current_cart['cart'][c][3],
                        current_cart['cart'][c][2] * current_cart['cart'][c][3],
                    )
                    for c in current_cart['cart']
                ]
            )
            delivery_map = {DLVR: 'Delivery', AWAY: 'Takeaway', REST: 'Restaurant'}
            delivery = delivery_map.get(current_cart['order_type'])
            pay_type = 'Cash' if call.data == 'order_proceed_cash' else 'PhonePe'
            comments = ''  # '\nКомментарий
            bot.send_message(
                managers[0],
                text='Новый заказ от @{} ({}):\n{}, {}\n{}{}'.format(
                    call.message.chat.username,
                    call.message.chat.id,
                    delivery,
                    pay_type,
                    cart_text,
                    comments,
                ),
            )
            m_ = bot.send_message(
                call.message.chat.id,
                text='Спасибо за ваш заказ! С вами свяжутся в ближайшее время',
            )
            track_and_clear_messages(m_)

            reset_settings(call.message.chat.id, soft=True)
            return
        elif call.data == 'go_back':
            # todo flush product_info
            if ':' not in curr_menu[call.message.chat.id]:
                curr_menu[call.message.chat.id] = None
            else:
                curr_menu[call.message.chat.id] = ':'.join(
                    curr_menu[call.message.chat.id].split(':')[:-1]
                )

        elif call.data.startswith('order_'):
            ordered_item = get_concrete_data(call.data[6:])
            name = call.data.split(':')[-1]
            content = ordered_item
            if name not in current_cart['cart']:
                content.append(1)  # amount
                content.append(call.data[6:])  # full path
                current_cart['cart'][name] = content
            else:
                current_cart['cart'][name][3] += 1
            # show_type = 'product'
        elif call.data.startswith('remove_order_'):
            # removed_item = get_concrete_data(call.data[13:])
            name = call.data.split(':')[-1]
            current_cart['cart'][name][3] -= 1
            if current_cart['cart'][name][3] <= 0:
                del current_cart['cart'][name]
            show_type = 'cart'
        show_menu(call.message, show_type)
    except Exception as e:
        logger('Callback exception! + ' + str(e))


bot.polling(none_stop=True, interval=0)
