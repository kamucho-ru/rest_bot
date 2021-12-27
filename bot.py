import telebot
from telebot import types

from data import *
from settings import *

lang = None
curr_menu = None
cart = {}

REST = 'REST'
AWAY = 'AWAY'
DLVR = 'DLVR'
cart_type = REST

CASH = 'CASH'
PHPE = 'PHNE'
pay_type = None

messages = []


bot = telebot.TeleBot(token)

def logger(message):
    global DEBUG
    if DEBUG:
        print(message)
    # else log somewhere else


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


def track_and_clear_messages(message, and_clear=True):
    global messages
    not_inserted = True
    logger('track message "{}" ({}), already there: [{}]'.format(
        message.text, message.id, [(m.text, m.id) for m in messages]
    ))
    for m in messages:
        if m.id == message.id:
            not_inserted = False

        if and_clear:
            try:
                bot.delete_message(m.chat.id, m.id)
            except Exception:
                logger('EXCEPTION WARNING while deleting message "{}" ({}): {}'.format(
                    m.text, m.id, e
                ))
            messages.remove(m)

    if not_inserted:
        messages.append(message)


def show_menu(message, show='menu'):
    logger('showing menu')
    global lang, curr_menu, menu, cart
    messages_stack = []

    def make_keyboard(current):
        keyboard = types.InlineKeyboardMarkup()

        def add_menu_buttons(submenu_data, prev_path):
            for i in submenu_data:
                if isinstance(submenu_data[i], list):
                    text_ = '{} [{}] / {}'.format(
                        i, submenu_data[i][0], submenu_data[i][2]
                    )
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
                    text=get_translation('Go to top menu'),
                    callback_data='open_menu'
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
        if cart:
            for c in cart:
                item_key = types.InlineKeyboardButton(
                    text=get_translation('{} [{}] * {} = {} rs.').format(
                        c, cart[c][0], cart[c][3], cart[c][2]*cart[c][3]
                    ),
                    callback_data='remove_order_{}'.format(cart[c][4]))
                keyboard.add(item_key)
        item_key = types.InlineKeyboardButton(
            text=get_translation('Proceed to order'),
            callback_data='order_proceed_2')
        keyboard.add(item_key)

    elif show == 'product':
        # show info about product and order buttons
        data = get_concrete_data(curr_menu)
        text = '***___{}___***</b>\n{}, {} rs.'.format(
            curr_menu.split(':')[-2],
            data[0],
            data[2]
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
            text=get_translation('Add 1'),
            callback_data=f'order_{curr_menu}'
        )
        keyboard.add(item_key)

        for i in cart:
            if cart[i][0] == data[0] and cart[i][2] == data[2]:
                if cart[i][3] > 0:
                    item_key = types.InlineKeyboardButton(
                        text=get_translation('Remove 1'),
                        callback_data=f'remove_order_{curr_menu}'
                    )
                    keyboard.add(item_key)

    else: #  if show == 'menu':
        # show current menu
        keyboard = make_keyboard(curr_menu)

    if cart and show != 'cart':
        cart_items = 0
        cart_price = 0
        for c in cart:
            cart_items += int(cart[c][3])
            cart_price += int(cart[c][3]) * int(cart[c][2])
        item_key = types.InlineKeyboardButton(
            text=get_translation('Cart: {} items = {} rs.').format(cart_items, cart_price),
            callback_data='order_proceed'
        )
        keyboard.add(item_key)

    # Назад или сразу полное меню
    if curr_menu:
        item_key = types.InlineKeyboardButton(
            text=get_translation('<< back'),
            callback_data='go_back'
        )
        keyboard.add(item_key)

    question = get_translation('Please select ')
    if curr_menu:
        question = curr_menu.lower().replace(':', ' > ')
    if show == 'cart':
        question = get_translation('Select positions for delete or proceed to order')

    track_and_clear_messages(message)

    for m in messages_stack:
        m_ = bot.send_message(message.chat.id, text=question)
        track_and_clear_messages(m_, False)
        question = m

    m_ = bot.send_message(message.chat.id, text=question, reply_markup=keyboard)
    track_and_clear_messages(m_)


def check_lang(user_id):
    global lang
    m_ = False
    if not lang:
        keyboard = types.InlineKeyboardMarkup()

        for lang, call in langs:
            lang_key = types.InlineKeyboardButton(text=lang, callback_data=call)
            keyboard.add(lang_key)
        question = '?'
        m_ = bot.send_message(user_id, text=question, reply_markup=keyboard)
        track_and_clear_messages(m_, False)
    logger(f'Language check for {user_id}: {True if m_ else False}')
    return m_


@bot.message_handler(content_types=['text'])  # ['text', 'document', 'audio']
def get_text_messages(message):
    logger('message received')
    global lang, DEBUG

    track_and_clear_messages(message)

    if message.text == '/clear':
        reset_settings()

    if DEBUG:
        known_ids = [
            NICK_ID, UZBEK_ID,
            488657210, #  Liza
        ]
        if message.chat.id not in known_ids:
            bot.send_message(NICK_ID, text='new customer {} {}'.format(
                message.from_user.id, message.from_user
            ))
            print('send to', message.chat.id)

    if not check_lang(message.chat.id):
        show_menu(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        logger('callback_worker from {} : {} [{}]'.format(
            call.message.chat.username, call.data, call.message.text
        ))
        global lang, curr_menu, cart, cart_type
        show_type = 'menu'

        check_lang(call.message.chat.id)

        if call.data.startswith('set_') and call.data.endswith('_lang'):
            # set language
            lang = call.data[4:-5]

        elif call.data == 'open_menu':
            # Show top
            curr_menu = None

        elif call.data.startswith('open_menu_'):
            # show submenu
            curr_menu = call.data[10:]

        elif call.data.startswith('open_item_'):
            # show product info
            show_type = 'product'
            curr_menu = call.data[10:]

        elif call.data == 'order_proceed':
            show_type = 'cart'
            # todo flush product_info

        elif call.data == 'order_proceed_2':
            keyboard = types.InlineKeyboardMarkup()

            item_key = types.InlineKeyboardButton(text=get_translation('Order at restaurant'),
                                                  callback_data='order_proceed_restaurant')
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(text=get_translation('Takeaway from restaurant'),
                                                  callback_data='order_proceed_takeaway')
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(text=get_translation('Delivery'),
                                                  callback_data='order_proceed_delivery')
            keyboard.add(item_key)

            text = get_translation('Choose order type')

            m_ = bot.send_message(call.message.chat.id, text=text, reply_markup=keyboard)
            track_and_clear_messages(m_)
            return
        elif call.data in [
            'order_proceed_delivery',
            'order_proceed_takeaway',
            'order_proceed_restaurant'
        ]:
            if call.data == 'order_proceed_delivery':
                cart_type = DLVR
                # если доставка - спросить локацию
            elif call.data == 'order_proceed_takeaway':
                cart_type = AWAY

            # show payment options
            # способ оплаты - кэш/phonepe
            keyboard = types.InlineKeyboardMarkup()

            item_key = types.InlineKeyboardButton(text=get_translation('Cash'),
                                                  callback_data='order_proceed_cash')
            keyboard.add(item_key)

            item_key = types.InlineKeyboardButton(text=get_translation('PhonePe'),
                                                  callback_data='order_proceed_phonepe')
            keyboard.add(item_key)

            text = get_translation('Choose payment type')

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
                        c, cart[c][0], cart[c][3], cart[c][2] * cart[c][3]
                    ) for c in cart
                ]
            )
            delivery_map = {
                DLVR: 'Delivery',
                AWAY: 'Takeaway',
                REST: 'Restaurant'
            }
            delivery = delivery_map.get(cart_type)
            pay_type = 'Cash' if call.data == 'order_proceed_cash' else 'PhonePe'
            comments = '' # '\nКомментарий
            bot.send_message(
                NICK_ID,
                text='Новый заказ от @{} ({}):\n{}, {}\n{}{}'.format(
                    call.message.chat.username, call.message.chat.id,
                    delivery, pay_type, cart_text, comments
                ),
            )
            m_ = bot.send_message(
                call.message.chat.id,
                text='Спасибо за ваш заказ! С вами свяжутся в ближайшее время'
            )
            track_and_clear_messages(m_)
            cart = {}
            curr_menu = None
            return
        elif call.data == 'go_back':
            # todo flush product_info
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
                content.append(call.data[6:])  # full path
                cart[name] = content
            else:
                cart[name][3] += 1
            # show_type = 'product'
        elif call.data.startswith('remove_order_'):
            # removed_item = get_concrete_data(call.data[13:])
            name = call.data.split(':')[-1]
            cart[name][3] -= 1
            if cart[name][3] <= 0:
                del cart[name]
            show_type = 'cart'
        show_menu(call.message, show_type)
    except Exception as e:
        logger(f'Callback exception! + {e}')


bot.polling(none_stop=True, interval=0)
