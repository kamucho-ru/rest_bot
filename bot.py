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
    #     'last_call': None
    # }
}

lang = {
    # 'user_id': 'smth'
}
curr_menu = {
    # 'user_id': 'smth'
}

menu_hash = {
    # hash for link strings woth dictionary
    # str( hash( 'Full menu:drinks:...') ): 'Full menu:drinks:...',
}


def get_menu_hash(path):
    # create hash for buttons text instead of full menu string
    global menu_hash
    _hash = str(hash(path))
    if _hash not in menu_hash:
        menu_hash[_hash] = path
    return _hash


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

known_users = {}
f = open('known_users.txt', 'r')
x = f.readline()  # headers
while x:
    x = f.readline()
    if '::' in x:
        x = x.replace('\n', '')
        user_id = int(x.split('::')[0])
        known_users[user_id] = {'username': x.split('::')[1], 'comment': x.split('::')[3]}
        lang[user_id] = x.split('::')[2] if x.split('::')[2] != 'None' else None

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
    if user_id in cart:
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
            'comments': [],
            'last_call': None,
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


def update_langs():
    global lang, known_users
    f = open('known_users.txt', 'w')
    f.write('#user_id::username::lang::comment\n')
    f.writelines(
        [
            '{}::{}::{}::{}\n'.format(
                x, known_users[x]['username'], lang[x], known_users[x]['comment']
            )
            for x in known_users
        ]
    )
    f.close()


def show_menu(message, show='menu'):
    logger('showing menu, type ' + show)
    global lang, curr_menu, menu, cart
    messages_stack = []
    current_cart = get_current_cart(message.chat.id)

    def make_keyboard(current):
        keyboard = types.InlineKeyboardMarkup()

        def add_menu_buttons(submenu_data, prev_path):
            for i in submenu_data:
                path = get_menu_hash(prev_path + i)
                if isinstance(submenu_data[i], list):
                    template_text = '{} / {}'
                    name = get_translation(i, message.chat.id)
                    text_ = template_text.format(name, submenu_data[i][2])
                    callback_ = 'open_item_' + path  # for showing product info
                    callback_ = 'order_' + path
                else:
                    text_ = get_translation(i, message.chat.id)
                    callback_ = 'open_menu_' + path

                item_key = types.InlineKeyboardButton(text=text_, callback_data=callback_)
                logger(f'::add "{text_}", callback "{callback_}"')
                keyboard.add(item_key)

        if current:
            keyboard.add(
                types.InlineKeyboardButton(
                    text=get_translation('Go to top menu', message.chat.id),
                    callback_data='open_menu',
                )
            )
        data_ = get_concrete_data(current)

        if isinstance(data_, dict):
            add_menu_buttons(data_, '' if not current else (current + ':'))
        else:
            logger('WARNING!! for path {current} not possible make menu (data type is not dict)')

        return keyboard

    if show == 'cart':
        # show cart content
        keyboard = types.InlineKeyboardMarkup()
        for c in current_cart['cart']:
            template_text = get_translation('{} * {} = {} rs.', message.chat.id)
            name = get_translation(c, message.chat.id)
            amount = str(current_cart['cart'][c][3])
            total = str(int(current_cart['cart'][c][2]) * int(current_cart['cart'][c][3]))
            item_key = types.InlineKeyboardButton(
                text=template_text.format(name, amount, total),
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
            text=get_translation('<< back', message.chat.id),
            callback_data='go_back' if show == 'menu' else 'open_menu_',
        )
        keyboard.add(item_key)
        question = ' > '.join(
            [
                get_translation(s, message.chat.id)
                for s in curr_menu.get(message.chat.id).split(':')
            ]
        )

    if show == 'cart':
        question = get_translation(
            'Select positions to delete or proceed to order', message.chat.id
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
    global DEBUG, curr_menu

    track_and_clear_messages(message)

    if message.chat.id not in known_users:
        f = open('known_users.txt', 'a')
        comment = 'Auto added'
        f.write(
            '{}::{}::{}::{}\n'.format(
                message.chat.id, message.chat.username, lang.get(message.chat.id, None), comment
            )
        )
        if not message.chat.username:
            bot.forward_message(managers[0], message.chat.id, message.id)
            bot.send_message(managers[0], text=f'Forwarded from {message.chat.id} {message.chat}')
            bot.forward_message(managers[1], message.chat.id, message.id)
            bot.send_message(managers[1], text=f'Forwarded from {message.chat.id} {message.chat}')
        known_users[message.chat.id] = {'username': message.chat.username, 'comment': comment}
        f.close()

    if message.text == '/menu':
        curr_menu[message.chat.id] = None
    elif message.text == '/clear':
        reset_settings(message.chat.id)
    else:
        current_cart = get_current_cart(message.chat.id)
        current_cart['comments'].append(message.text)

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
        current_cart['last_call'] = call.data

        check_lang(call.message.chat.id)

        # set language
        if call.data.startswith('set_') and call.data.endswith('_lang'):
            lang[call.message.chat.id] = call.data[4:-5]
            update_langs()
            # todo ask name, phone

        # show top section
        elif call.data == 'open_menu':
            curr_menu[call.message.chat.id] = None

        # show submenu
        elif call.data.startswith('open_menu_'):
            if call.data[10:]:
                curr_menu[call.message.chat.id] = menu_hash[call.data[10:]]

        # show product info
        # elif call.data.startswith('open_item_'):
        #     show_type = 'product'
        #     curr_menu[call.message.chat.id] = call.data[10:]

        # add product to cart (one per time)
        elif call.data.startswith('order_') and not call.data.startswith('order_proceed'):
            full_path = menu_hash[call.data[6:]]
            ordered_item = get_concrete_data(full_path)
            name = full_path.split(':')[-1]
            content = ordered_item
            if name not in current_cart['cart']:
                content.append(1)  # amount
                content.append(full_path)  # full path
                current_cart['cart'][name] = content
            else:
                current_cart['cart'][name][3] += 1
            # todo add detection, from where we add product: cart or menu
            # show_type = 'product'

        # remove product from cart
        elif call.data.startswith('remove_order_') and current_cart['cart']:
            # removed_item = get_concrete_data(call.data[13:])
            name = call.data.split(':')[-1]
            current_cart['cart'][name][3] -= 1
            if current_cart['cart'][name][3] <= 0:
                del current_cart['cart'][name]
            show_type = 'cart'

        # show cart for confirmation
        elif call.data == 'order_proceed':
            show_type = 'cart'
            # todo flush product_info

        # ask if any extra wishings
        elif call.data == 'order_proceed_2' and current_cart['cart']:
            '''
            keyboard = types.InlineKeyboardMarkup()

            item_key = types.InlineKeyboardButton(
                text=get_translation('No, proceed', call.message.chat.id), callback_data='order_proceed_3'
            )
            keyboard.add(item_key)

            m_ = bot.send_message(
                call.message.chat.id,
                text=get_translation('Do you have any extra wishes?', call.message.chat.id),
                reply_markup=keyboard
            )
            track_and_clear_messages(m_)
            return

        # suggest to choose type of delivery
        elif call.data == 'order_proceed_3' and current_cart['cart']:
            '''
            keyboard = types.InlineKeyboardMarkup()

            item_key = types.InlineKeyboardButton(
                text=get_translation('Proceed at the restaurant', call.message.chat.id),
                callback_data='order_proceed_restaurant',
            )
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(
                text=get_translation('Wish to takeaway', call.message.chat.id),
                callback_data='order_proceed_takeaway',
            )
            keyboard.add(item_key)

            # item_key = types.InlineKeyboardButton(
            #     text=get_translation('I will be there in ..', call.message.chat.id),
            #     callback_data='order_proceed_delay',
            # )
            # keyboard.add(item_key)

            # item_key = types.InlineKeyboardButton(
            #     text=get_translation('Delivery', call.message.chat.id),
            #     callback_data='order_proceed_delivery',
            # )
            # keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(
                text=get_translation('<< back', call.message.chat.id), callback_data='open_menu_'
            )
            keyboard.add(item_key)

            text = get_translation(
                'You are welcome at <a href="https://www.google.com/maps/place/Mozogao+Bar+'
                '%26+Restaurant/@15.654396,73.7527975,21z/data=!4m5!3m4!1s0x3bbfec1ec5e2714b:'
                '0x6ec5c26f0656f0de!8m2!3d15.6543352!4d73.7528804">MozoGao</a>. '
                'Your order will be ready as soon as it is possible.\nWhat are you prefer?',
                call.message.chat.id,
            )

            m_ = bot.send_location(call.message.chat.id, 15.654315282911606, 73.75289136506875)
            track_and_clear_messages(m_)

            m_ = bot.send_message(
                call.message.chat.id, text=text, reply_markup=keyboard, parse_mode='HTML'
            )
            track_and_clear_messages(m_, False)

            return

        # Under processing
        elif (
            call.data
            in [
                'order_proceed_delivery',
                'order_proceed_delay',
                'order_proceed_takeaway',
                'order_proceed_restaurant',
            ]
            and current_cart['cart']
        ):
            if call.data == 'order_proceed_delivery':
                current_cart['order_type'] = DLVR
                # если доставка - спросить локацию
            elif call.data == 'order_proceed_takeaway':
                current_cart['order_type'] = AWAY

            '''   Пока что закомментировать всё остальное. Лишнее

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

        # todo ask for promocode or smth discount
        elif call.data == 'order_proceed_4' and current_cart['cart']:
            # скидка 10%? - промокод или ссылка на отзыв (скриншот)
            pass

        # Confirm order, send messages for everyone
        elif call.data in ['order_proceed_cash', 'order_proceed_phonepe'] and current_cart['cart']:
            '''

            # сообщение менеджерам о новом заказе
            cart_text = '\n'.join(
                [
                    '{} [{}] x {} = {} rs.'.format(
                        c,
                        current_cart['cart'][c][0],
                        current_cart['cart'][c][3],
                        int(current_cart['cart'][c][2]) * int(current_cart['cart'][c][3]),
                    )
                    for c in current_cart['cart']
                ]
            )
            amount = sum(
                [
                    int(current_cart['cart'][c][2]) * int(current_cart['cart'][c][3])
                    for c in current_cart['cart']
                ]
            )
            delivery_map = {DLVR: 'Delivery', AWAY: 'Takeaway', REST: 'Restaurant'}
            delivery = delivery_map.get(current_cart['order_type'])
            pay_type = ''  # 'Cash' if call.data == 'order_proceed_cash' else 'PhonePe'
            comments = (
                ''
            )  # '\nПожелания:\n'+'\n'.join(current_cart['comments']) if current_cart['comments'] else ''
            for m in managers:
                bot.send_message(
                    m,
                    text='New order from @{} ({}):\n{} {}\n{}\nTotal: {} rs.{}'.format(
                        call.message.chat.username,
                        call.message.chat.id,
                        delivery,
                        pay_type,
                        cart_text,
                        amount,
                        comments,
                    ),
                )
            m_ = bot.send_message(
                call.message.chat.id,
                text=get_translation(
                    'Your order is:\n{}\nTotal amount: {} rs.', call.message.chat.id
                ).format(cart_text, amount),
            )
            track_and_clear_messages(m_)

            m_ = bot.send_message(
                call.message.chat.id,
                text=get_translation(
                    'Thank you for your order! Our managers will reach you soon',
                    call.message.chat.id,
                ),
            )
            track_and_clear_messages(m_, False)

            reset_settings(call.message.chat.id, soft=True)
            return

        # return up in the menu
        elif call.data == 'go_back':
            # todo flush product_info
            if call.message.chat.id not in curr_menu or ':' not in curr_menu[call.message.chat.id]:
                curr_menu[call.message.chat.id] = None
            else:
                curr_menu[call.message.chat.id] = ':'.join(
                    curr_menu[call.message.chat.id].split(':')[:-1]
                )

        show_menu(call.message, show_type)
    except Exception as e:
        logger('Callback exception! + ' + str(e) + ', ' + str(e.__dict__))
        m_ = bot.send_message(call.message.chat.id, text='Oops, something went wrong!')
        track_and_clear_messages(m_, False)
        curr_menu[call.message.chat.id] = None
        show_menu(call.message, 'menu')


bot.polling(none_stop=True, interval=0)
